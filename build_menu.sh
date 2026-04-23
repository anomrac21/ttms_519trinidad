# Sync submodule URLs from .gitmodules to ensure HTTPS URLs are used
git submodule sync --recursive

# Initialize submodules with HTTPS URLs
git submodule update --init --recursive

# Update submodules to latest master branch to ensure latest theme changes are included
echo "Updating submodules to latest master branch..."
cd themes/_menus_ttms
git fetch origin master
git checkout master
git pull origin master
cd ../..

# Register client site with auth-service (if not exists)
if [ -f "scripts/register-client.sh" ]; then
    echo "Registering client site with auth-service..."
    bash scripts/register-client.sh
fi

# Build the Hugo site with optimization
echo "Running Hugo build with minification..."
hugo --gc --minify

echo "✅ Build completed successfully!"
