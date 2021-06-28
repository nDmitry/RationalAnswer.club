from django.contrib.sitemaps import Sitemap

from posts.models.post import Post


class PublicPostsSitemap(Sitemap):
    protocol = "https"

    def items(self):
        return Post.visible_objects().filter(is_public=True)

    def lastmod(self, obj: Post):
        return obj.updated_at


sitemaps = {
    "public_posts": PublicPostsSitemap,
}
