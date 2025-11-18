#!/bin/bash
# Script to download vendor assets from CDN to local static files
# This removes external CDN dependencies and fixes CSP violations

set -e

STATIC_DIR="/home/user/FlaskBlog/app/static/vendor"

echo "Downloading vendor assets..."

# Note: Tailwind CSS is included in DaisyUI, no separate download needed

# Download DaisyUI CSS (includes full Tailwind CSS utilities)
echo "Downloading DaisyUI..."
curl -sL "https://cdn.jsdelivr.net/npm/daisyui@4.6.0/dist/full.min.css" \
  -o "${STATIC_DIR}/daisyui/daisyui.min.css"

# Download DaisyUI themes
curl -sL "https://cdn.jsdelivr.net/npm/daisyui@4.6.0/dist/themes.min.css" \
  -o "${STATIC_DIR}/daisyui/themes.min.css"

# Download Tabler Icons CSS
echo "Downloading Tabler Icons..."
curl -sL "https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@2.46.0/tabler-icons.min.css" \
  -o "${STATIC_DIR}/tabler-icons/tabler-icons.min.css"

# Download Tabler Icons fonts
mkdir -p "${STATIC_DIR}/tabler-icons/fonts"
curl -sL "https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@2.46.0/fonts/tabler-icons.woff2" \
  -o "${STATIC_DIR}/tabler-icons/fonts/tabler-icons.woff2"
curl -sL "https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@2.46.0/fonts/tabler-icons.woff" \
  -o "${STATIC_DIR}/tabler-icons/fonts/tabler-icons.woff"
curl -sL "https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@2.46.0/fonts/tabler-icons.ttf" \
  -o "${STATIC_DIR}/tabler-icons/fonts/tabler-icons.ttf"

# Download ApexCharts (disable certificate check as workaround)
echo "Downloading ApexCharts..."
curl -skL "https://cdn.jsdelivr.net/npm/apexcharts@3.45.2/dist/apexcharts.min.js" \
  -o "${STATIC_DIR}/apexcharts/apexcharts.min.js"

# Update Tabler Icons CSS to use local fonts
sed -i 's|https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@2.46.0/fonts/|fonts/|g' \
  "${STATIC_DIR}/tabler-icons/tabler-icons.min.css"

# Remove source map references from all CSS files (not needed for production)
echo "Removing source map references..."
sed -i 's|/\*# sourceMappingURL=.*\.map \*/||g' "${STATIC_DIR}/daisyui/daisyui.min.css"
sed -i 's|/\*# sourceMappingURL=.*\.map \*/||g' "${STATIC_DIR}/daisyui/themes.min.css"
sed -i 's|/\*# sourceMappingURL=.*\.map \*/||g' "${STATIC_DIR}/tabler-icons/tabler-icons.min.css"

echo "✓ All vendor assets downloaded successfully!"
echo ""
echo "File sizes:"
ls -lh "${STATIC_DIR}"/*/*.{css,js} 2>/dev/null | awk '{print $5 "\t" $9}' || true
echo ""
echo "Total size:"
du -sh "${STATIC_DIR}"
