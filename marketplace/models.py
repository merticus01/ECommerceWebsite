from django.conf import settings
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    is_buyer = models.BooleanField(default=False)
    is_seller = models.BooleanField(default=False)

    class Meta:
        swappable = 'AUTH_USER_MODEL'

class SellerProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="seller_profile",
    )
    display_name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    location = models.CharField(max_length=120, blank=True)
    years_active = models.PositiveIntegerField(default=0)
    bio = models.TextField(blank=True)
    curation_style = models.TextField(blank=True)
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["display_name"]

    def __str__(self) -> str:
        return self.display_name

    def get_absolute_url(self):
        return reverse("seller_detail", args=[self.slug])


class Era(models.TextChoices):
    FIFTIES = "1950s", "50s"
    SIXTIES = "1960s", "60s"
    SEVENTIES = "1970s", "70s"
    EIGHTIES = "1980s", "80s"
    NINETIES = "1990s", "90s"
    Y2K = "2000s", "Y2K"


class Condition(models.TextChoices):
    NEW_OLD_STOCK = "new_old_stock", "New Old Stock"
    EXCELLENT = "excellent", "Excellent"
    GOOD = "good", "Good"
    FAIR = "fair", "Fair"


class Category(models.TextChoices):
    CLOTHING = "clothing", "Clothing & Accessories"
    JEWELRY = "jewelry", "Jewelry"
    HOME = "home_decor", "Home Décor"
    ART = "art_collectibles", "Art & Collectibles"
    FURNITURE = "furniture", "Furniture"
    MEDIA = "media", "Cameras, Vinyl, Books"
    DESIGNER = "designer_archive", "Designer Archive"


class Product(models.Model):
    seller = models.ForeignKey(
        SellerProfile, on_delete=models.CASCADE, related_name="products"
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    era = models.CharField(max_length=20, choices=Era.choices)
    category = models.CharField(max_length=30, choices=Category.choices)
    condition = models.CharField(
        max_length=20, choices=Condition.choices, default=Condition.GOOD
    )
    description = models.TextField()
    story = models.TextField(
        blank=True,
        help_text="Share the provenance, history, or story behind this piece.",
    )
    measurements = models.CharField(max_length=255, blank=True)
    materials = models.CharField(max_length=255, blank=True)
    sustainability_tags = models.CharField(
        max_length=255,
        blank=True,
        help_text="Comma-separated tags like 'deadstock, upcycled, locally sourced'.",
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    inventory = models.PositiveIntegerField(default=1)
    product_image = models.FileField(upload_to='media')

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self):
        return reverse("product_detail", args=[self.slug])


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="products/")
    alt_text = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self) -> str:
        return f"Image for {self.product.title}"


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="favorites"
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="favorited_by"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "product")


class SellerFollow(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="following"
    )
    seller = models.ForeignKey(
        SellerProfile, on_delete=models.CASCADE, related_name="followers"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "seller")


class Cart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="carts",
        null=True,
        blank=True,
    )
    session_key = models.CharField(max_length=40, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart {self.pk}"

    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name="items"
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def subtotal(self):
        return self.product.price * self.quantity


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        SHIPPED = "shipped", "Shipped"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="orders"
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    payment_reference = models.CharField(max_length=120, blank=True)

    def __str__(self):
        return f"Order #{self.pk}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items"
    )
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    seller = models.ForeignKey(SellerProfile, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def subtotal(self):
        return self.price * self.quantity


class EditorialArticle(models.Model):
    class ArticleType(models.TextChoices):
        STORY = "story", "Behind the Piece"
        SPOTLIGHT = "spotlight", "Seller Spotlight"
        ERA_GUIDE = "era_guide", "Era Guide"
        CARE_TIPS = "care_tips", "Care Tips"

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    type = models.CharField(max_length=20, choices=ArticleType.choices)
    hero_image = models.ImageField(upload_to="editorial/", blank=True)
    excerpt = models.TextField()
    body = models.TextField()
    featured_product = models.ForeignKey(
        Product,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="featured_in_articles",
    )
    seller = models.ForeignKey(
        SellerProfile,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="articles",
    )
    published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("editorial_detail", args=[self.slug])


