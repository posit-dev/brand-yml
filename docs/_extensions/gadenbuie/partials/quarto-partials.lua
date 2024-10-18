--[[
# Quarto Partials

Repo: https://github.com/gadenbuie/quarto-partials/
Docs: https://pkg.garrickadenbuie.com/quarto-partials/

# MIT License

Copyright (c) 2024 Garrick Aden-Buie

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
]]

local lustache = require("lustache")

--@param obj table
--@return table | string
local function pandoc_stringify(obj)
  if pandoc.utils.type(obj) == "string" or pandoc.utils.type(obj) == "Inlines" then
    return pandoc.utils.stringify(obj)
  end

  if type(obj) == "table" then
    for k, v in pairs(obj) do
      obj[k] = pandoc.utils.stringify(v)
    end
    return obj
  else
    return pandoc.utils.stringify(obj)
  end
end

function copy(obj, seen)
  if type(obj) ~= 'table' then return obj end
  if seen and seen[obj] then return seen[obj] end
  local s = seen or {}
  local res = setmetatable({}, getmetatable(obj))
  s[obj] = res
  for k, v in pairs(obj) do res[copy(k, s)] = copy(v, s) end
  return res
end

local function render_partial(file, data, context)
  local f = io.open(file, "r")
  local template = f:read("a")
  f:close()

  local rendered = lustache:render(template, data)

  -- if context is text (but in case new contexts are added)
  if context ~= "block" and context ~= "inline" then
    return pandoc.Str(rendered)
  end

  if string.match(file, "%.qmd") then
    -- And `.qmd` through Quarto
    if context == "block" then
      return quarto.utils.string_to_blocks(rendered)
    elseif context == "inline" then
      return quarto.utils.string_to_inlines(rendered)
    end

  elseif string.match(file, "%.md") or string.match(file, "%.txt") then
    -- Render `.md` through Pandoc
rendered = pandoc.read(rendered)
    if context == "inline" then
      return pandoc.utils.stringify(rendered)
    end
    return rendered.blocks

    
  elseif string.match(file, "%.tex")  then
    -- Limit `.tex` to LaTeX documents
    if context == "inline" then
      return pandoc.RawBlock('tex', rendered)
    end
    return pandoc.RawBlock('tex', rendered)
  
  elseif string.match(file, "%.html") then
    -- And `.html` for HTML documents
    if context == "inline" then
      return pandoc.RawInline('html', rendered)
    end
    return pandoc.RawBlock('html', rendered)
  end
  
  return rendered
end

local function quarto_partial(args, kwargs, meta, raw_args, context)
  local partial_data = {}
  local data = {}
  local partial_key = "partial-data"

  if #args > 1 then
    -- start partial_data with a copy of `meta`
    partial_data = copy(meta)
    partial_key = args[2]
    local partial_keys = string.split(partial_key, "%.")
  
    for _, key in ipairs(partial_keys) do
      if partial_data[key] then
        partial_data = copy(partial_data[key])
      else
        msg = "Could not find partial data key in YAML metadata: " .. partial_key
        quarto.log.error(msg)
        assert(false, msg)
      end
    end
  elseif meta[partial_key] then
    partial_data = copy(meta[partial_key])
  end

  if #partial_data > 0 then
    local data_str = pandoc_stringify(partial_data)

    if type(data_str) == "string" then
      quarto.log.error("Please choose a metadata key from your YAML frontmatter that contains a table of partial data.")
      assert(false, "Expected a table of partial data in YAML frontmatter key " .. partial_key)
    end

    data = data_str
  end

  for k, v in pairs(kwargs) do
    local v_is_json_string = false
    if pandoc.utils.type(v) == "string" then
      v_is_json_string = string.match(v, "^%[") or string.match(v, "^{")
    end
    
    if v_is_json_string then
      data[k] = quarto.json.decode(v)
    else
      data[k] = v
    end
  end


  return render_partial(args[1], data, context)
end

return {
  ["partial"] = quarto_partial
}
