"""Supplier finder module for Supply Chain Service."""

import math
from typing import Optional
from uuid import UUID, uuid4

import structlog

from ..core.config import settings

logger = structlog.get_logger()


class SupplierFinder:
    """Find and compare suppliers for products."""

    def __init__(self) -> None:
        """Initialize supplier finder."""
        self._mock_suppliers = self._init_mock_suppliers()

    def _init_mock_suppliers(self) -> list[dict]:
        """Initialize mock supplier data."""
        return [
            {
                "id": uuid4(),
                "name": "Al-Rashid Agricultural Supplies",
                "name_ar": "مستلزمات الراشد الزراعية",
                "latitude": 24.7136,
                "longitude": 46.6753,
                "rating": 4.8,
                "delivery_days": 2,
                "price_modifier": 1.0,
            },
            {
                "id": uuid4(),
                "name": "Green Fields Trading",
                "name_ar": "تجارة الحقول الخضراء",
                "latitude": 21.4858,
                "longitude": 39.1925,
                "rating": 4.5,
                "delivery_days": 3,
                "price_modifier": 0.95,
            },
            {
                "id": uuid4(),
                "name": "Sahara Agro Solutions",
                "name_ar": "حلول صحارى الزراعية",
                "latitude": 26.4207,
                "longitude": 50.0888,
                "rating": 4.3,
                "delivery_days": 4,
                "price_modifier": 0.90,
            },
            {
                "id": uuid4(),
                "name": "Farm Fresh Supplies",
                "name_ar": "مستلزمات المزرعة الطازجة",
                "latitude": 24.1500,
                "longitude": 47.3000,
                "rating": 4.6,
                "delivery_days": 1,
                "price_modifier": 1.05,
            },
        ]

    @staticmethod
    def _haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points in kilometers."""
        R = 6371  # Earth's radius in kilometers

        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)

        a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    async def find_suppliers_by_product(
        self,
        product_id: UUID,
        latitude: float | None = None,
        longitude: float | None = None,
        max_results: int = 10,
    ) -> list[dict]:
        """Find suppliers that carry a specific product.

        Args:
            product_id: Product UUID
            latitude: Optional farmer latitude for distance sorting
            longitude: Optional farmer longitude for distance sorting
            max_results: Maximum number of results

        Returns:
            List of supplier dictionaries
        """
        logger.info(
            "finding_suppliers_by_product",
            product_id=str(product_id),
            has_location=latitude is not None,
        )

        suppliers = self._mock_suppliers.copy()

        # Sort by distance if location provided
        if latitude is not None and longitude is not None:
            for supplier in suppliers:
                supplier["distance_km"] = self._haversine_distance(
                    latitude, longitude, supplier["latitude"], supplier["longitude"]
                )
            suppliers.sort(key=lambda s: s["distance_km"])

        return suppliers[:max_results]

    async def find_suppliers_nearby(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 50.0,
    ) -> list[dict]:
        """Find suppliers within a radius.

        Args:
            latitude: Center latitude
            longitude: Center longitude
            radius_km: Search radius in kilometers

        Returns:
            List of nearby supplier dictionaries
        """
        logger.info(
            "finding_nearby_suppliers",
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km,
        )

        nearby = []
        for supplier in self._mock_suppliers:
            distance = self._haversine_distance(latitude, longitude, supplier["latitude"], supplier["longitude"])
            if distance <= radius_km:
                supplier_copy = supplier.copy()
                supplier_copy["distance_km"] = round(distance, 2)
                nearby.append(supplier_copy)

        # Sort by distance
        nearby.sort(key=lambda s: s["distance_km"])

        return nearby

    async def compare_prices(
        self,
        product_id: UUID,
        quantity: float,
        supplier_ids: list[UUID] | None = None,
    ) -> list[dict]:
        """Compare prices from multiple suppliers.

        Args:
            product_id: Product UUID
            quantity: Quantity needed
            supplier_ids: Optional list of specific suppliers to compare

        Returns:
            List of price comparisons sorted by total price
        """
        logger.info(
            "comparing_prices",
            product_id=str(product_id),
            quantity=quantity,
        )

        import random

        comparisons = []
        base_price = random.uniform(10, 50)

        for supplier in self._mock_suppliers:
            if supplier_ids and supplier["id"] not in supplier_ids:
                continue

            unit_price = round(base_price * supplier["price_modifier"], 2)
            total_price = round(unit_price * quantity, 2)

            comparisons.append(
                {
                    "supplier_id": supplier["id"],
                    "supplier_name": supplier["name"],
                    "supplier_name_ar": supplier["name_ar"],
                    "unit_price": unit_price,
                    "total_price": total_price,
                    "delivery_days": supplier["delivery_days"],
                    "rating": supplier["rating"],
                }
            )

        # Sort by total price
        comparisons.sort(key=lambda c: c["total_price"])

        return comparisons

    async def check_availability(
        self,
        product_id: UUID,
        quantity: float,
        supplier_id: UUID,
    ) -> dict:
        """Check product availability at a supplier.

        Args:
            product_id: Product UUID
            quantity: Quantity needed
            supplier_id: Supplier UUID

        Returns:
            Availability information
        """
        logger.info(
            "checking_availability",
            product_id=str(product_id),
            quantity=quantity,
            supplier_id=str(supplier_id),
        )

        import random

        # Mock availability check
        available_quantity = random.uniform(quantity * 0.5, quantity * 2)
        is_available = available_quantity >= quantity

        return {
            "product_id": product_id,
            "supplier_id": supplier_id,
            "requested_quantity": quantity,
            "available_quantity": round(available_quantity, 2),
            "is_available": is_available,
            "status": "in_stock" if is_available else "limited",
            "estimated_restock_days": None if is_available else random.randint(3, 7),
        }

    async def get_quotes(
        self,
        product_id: UUID,
        quantity: float,
    ) -> list[dict]:
        """Get quotes from all available suppliers.

        Args:
            product_id: Product UUID
            quantity: Quantity needed

        Returns:
            List of quotes
        """
        logger.info(
            "getting_quotes",
            product_id=str(product_id),
            quantity=quantity,
        )

        import random

        quotes = []
        base_price = random.uniform(10, 50)

        for supplier in self._mock_suppliers:
            unit_price = round(base_price * supplier["price_modifier"], 2)
            total_price = round(unit_price * quantity, 2)

            quotes.append(
                {
                    "supplier_id": supplier["id"],
                    "supplier_name": supplier["name"],
                    "supplier_name_ar": supplier["name_ar"],
                    "unit_price": unit_price,
                    "total_price": total_price,
                    "delivery_days": supplier["delivery_days"],
                    "availability": random.choice(["in_stock", "limited", "in_stock"]),
                    "rating": supplier["rating"],
                }
            )

        return quotes

    async def find_best_supplier(
        self,
        product_id: UUID,
        quantity: float,
        optimize_for: str = "price",
        latitude: float | None = None,
        longitude: float | None = None,
    ) -> dict | None:
        """Find the best supplier based on optimization criteria.

        Args:
            product_id: Product UUID
            quantity: Quantity needed
            optimize_for: Optimization criteria (price, delivery, rating)
            latitude: Optional farmer latitude
            longitude: Optional farmer longitude

        Returns:
            Best supplier or None
        """
        logger.info(
            "finding_best_supplier",
            product_id=str(product_id),
            quantity=quantity,
            optimize_for=optimize_for,
        )

        quotes = await self.get_quotes(product_id, quantity)

        if not quotes:
            return None

        # Filter only available
        available_quotes = [q for q in quotes if q["availability"] != "out_of_stock"]

        if not available_quotes:
            return None

        if optimize_for == "price":
            return min(available_quotes, key=lambda q: q["total_price"])
        elif optimize_for == "delivery":
            return min(available_quotes, key=lambda q: q["delivery_days"])
        elif optimize_for == "rating":
            return max(available_quotes, key=lambda q: q["rating"])
        else:
            # Default to price
            return min(available_quotes, key=lambda q: q["total_price"])

    async def get_supplier_rating(self, supplier_id: UUID) -> dict | None:
        """Get supplier rating and review summary.

        Args:
            supplier_id: Supplier UUID

        Returns:
            Rating information or None
        """
        for supplier in self._mock_suppliers:
            if supplier["id"] == supplier_id:
                return {
                    "supplier_id": supplier_id,
                    "rating": supplier["rating"],
                    "total_reviews": 100,
                    "rating_breakdown": {
                        "5": 60,
                        "4": 25,
                        "3": 10,
                        "2": 3,
                        "1": 2,
                    },
                }

        return None
