set -o errexit   # abort on nonzero exitstatus

echo "Copying files to _site"
mkdir -p _site/schema
cp ../schema/brand.schema.yml _site/schema
cp ../schema/brand.schema.json _site/schema
mkdir -p _site/.well-known
cp articles/llm-brand-yml-prompt/brand-yml.prompt.txt _site/.well-known/llms.txt
