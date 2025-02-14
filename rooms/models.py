from django.utils import timezone
from django.db import models
from django.urls import reverse
from django_countries.fields import CountryField
from core.models import AbstractTimeStamped
from cal import Calendar

class AbstractItem(AbstractTimeStamped):

    """Abstract Item"""

    name = models.CharField(max_length=80)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class RoomType(AbstractItem):

    """RoomType Model Definition"""

    class Meta:
        verbose_name = "Room Type"


class Amenity(AbstractItem):

    """Amenity Model Definition"""

    class Meta:
        verbose_name_plural = "Amenities"


class Facility(AbstractItem):
    """Facility Model Definition"""

    class Meta:
        verbose_name_plural = "Facilities"


class HouseRule(AbstractItem):
    """HouseRule Model Definition"""

    class Meta:
        verbose_name = "House Rule"


class Photo(AbstractTimeStamped):
    """Photo Model Definition"""

    caption = models.CharField(max_length=80)
    file = models.ImageField(upload_to="room_photos")
    room = models.ForeignKey("Room", on_delete=models.CASCADE, related_name="photos")

    def __str__(self):
        return self.caption


class Room(AbstractTimeStamped):

    """Room Model Definition"""

    name = models.CharField(max_length=140)
    description = models.TextField()
    country = CountryField()
    city = models.CharField(max_length=80)
    price = models.IntegerField()
    address = models.CharField(max_length=140)
    guests = models.IntegerField(help_text="How many people will be staying?")
    beds = models.IntegerField()
    baths = models.IntegerField()
    bedrooms = models.IntegerField()
    check_in = models.TimeField()
    check_out = models.TimeField()
    instant_book = models.BooleanField(default=False)
    host = models.ForeignKey(
        "users.User", on_delete=models.PROTECT, related_name="rooms"
    )
    room_type = models.ForeignKey(
        "RoomType", on_delete=models.SET_NULL, null=True, related_name="rooms"
    )
    amenities = models.ManyToManyField(Amenity, blank=True, related_name="rooms")
    facilities = models.ManyToManyField(Facility, blank=True, related_name="rooms")
    house_rules = models.ManyToManyField(HouseRule, blank=True, related_name="rooms")

    def __str__(self):
        return self.name

    # 어떤 상황이든(콘솔, 어드민, 뷰 등) 모델이 변경되면 저장하는 메서드
    def save(self, *args, **kwargs):
        # self.city = self.city[0].upper() + self.city[1:]
        # self.city = self.city.capitalize()
        self.city = self.city.title()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("rooms:detail", kwargs={"pk": self.pk})

    def total_rating(self):

        all_reviews = self.reviews.all()
        all_ratings = 0
        for review in all_reviews:
            all_ratings += review.rating_average()
        try:
            return round(all_ratings / len(all_reviews), 2)

        except ZeroDivisionError:
            return 0

    def first_photo(self):
        try:
            photo, = self.photos.all()[:1]  # array의 원소를 변수에 할당하는 방법, unpacking values 라고 함
            return photo.file.url           # photo는 더이상 queryset이 아니고 인스턴스가 됨
        except ValueError:
            return None

    def get_next_four_photos(self):
        photos =  self.photos.all()[1:5]
        return photos
    
    def get_calendars(self):
        now = timezone.now()
        this_year = now.year
        this_month = now.month
        next_month = this_month + 1
        next_year = this_year
        if this_month == 12:
            next_month = 1
            next_year = this_year + 1
        this_month_cal = Calendar(this_year, this_month)
        next_month_cal = Calendar(next_year, next_month)
        return [this_month_cal, next_month_cal]