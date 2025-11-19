"""
This module provides a default banner for posts that don't have a custom banner.
"""

from io import BytesIO
from PIL import Image, ImageDraw, ImageFont


class DefaultBanner:
    """
    Generates a default banner image for posts.
    """

    @staticmethod
    def generate_default_banner(width=1200, height=630):
        """
        Generate a default banner image with a gradient background.

        Args:
            width (int): Width of the banner in pixels (default: 1200)
            height (int): Height of the banner in pixels (default: 630)

        Returns:
            bytes: PNG image data as bytes
        """
        # Create a new image with a dark gradient
        image = Image.new("RGB", (width, height))
        draw = ImageDraw.Draw(image)

        # Create a gradient from dark gray to black
        for y in range(height):
            # Calculate gradient color (from #2d3748 to #1a202c)
            r = int(45 - (45 - 26) * y / height)
            g = int(55 - (55 - 32) * y / height)
            b = int(72 - (72 - 44) * y / height)
            draw.line([(0, y), (width, y)], fill=(r, g, b))

        # Add subtle diagonal lines pattern
        for i in range(0, width + height, 40):
            draw.line(
                [(i, 0), (i - height, height)],
                fill=(255, 255, 255, 5),
                width=1,
            )

        # Convert image to bytes
        buffer = BytesIO()
        image.save(buffer, format="PNG", optimize=True)
        return buffer.getvalue()

    @staticmethod
    def get_cached_default_banner():
        """
        Get the default banner, cached as a module-level variable.

        Returns:
            bytes: PNG image data as bytes
        """
        if not hasattr(DefaultBanner, "_cached_banner"):
            DefaultBanner._cached_banner = DefaultBanner.generate_default_banner()
        return DefaultBanner._cached_banner
