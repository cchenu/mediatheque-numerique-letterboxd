"""Types for the project."""

from typing import Literal, TypedDict


class DataMediatheque(TypedDict):
    """Raw data get directly from the Mediatheque numerique website."""

    id: str
    uuid: str
    noQuotas: bool
    hasAudioDescription: bool
    productType: Literal["PROGRAM", "SERIE", "PACK"]
    productionYear: int | None
    duration: int | None  # In seconds
    outOfCatalog: bool
    movieType: Literal["LONG", "COURT", "MOYEN"] | None
    gradeAverage: float
    transactionsCount: int
    gradeCount: int
    title: str
    titleLanguage: str | None  # For example "fr"
    description: str | None
    slug: str
    episode: bool
    stsm: bool
    seasonsCount: int
    thumbFinalUrl: str | None
    posterFinalUrl: str | None
    directors: list[str] | None
    actors: list[str] | None
    cinetek: bool
    campus: bool
    storyCountries: list[str] | None  # For example ["FR"]
    productionCountries: list[str] | None  # For example ["FR"]
    qualities: list[Literal["SD", "HD"]] | None
    rating: float | None
    releaseDate: int | None
    trailerFinalUrl: str | None


class ProductsMediatheque(TypedDict):
    """Type for key `products` in JsonMediatheque."""

    content: list[DataMediatheque]


class ContentMediatheque(TypedDict):
    """Type for key `content` in JsonMediatheque."""

    products: ProductsMediatheque


class JsonMediatheque(TypedDict):
    """Type for `response.json()` after request to Mediatheque website."""

    content: ContentMediatheque


class Payload(TypedDict):
    """Type for `payload` variable."""

    withAggregations: bool
    includedProductCategoriesUuids: list[str]
    sortType: str
    pageNumber: int
    pageSize: int
