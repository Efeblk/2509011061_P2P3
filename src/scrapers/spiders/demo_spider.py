"""
Demo spider with realistic Turkish theater events.
Use this to demonstrate the full system with realistic data.
"""

from src.scrapers.spiders.base import BaseEventSpider
from src.scrapers.items import EventItem
import scrapy


class DemoSpider(BaseEventSpider):
    """
    Demo spider with realistic Turkish theater events.
    Creates 20 realistic events to showcase the system.
    """

    name = "demo"

    def start_requests(self):
        """Generate dummy request."""
        yield scrapy.Request(
            url="http://example.com",
            callback=self.parse,
            dont_filter=True,
            errback=lambda x: None,
        )

    def parse(self, response):
        """Generate realistic demo events."""

        # Real Turkish theater events for demo
        demo_events = [
            # Zorlu PSM Events
            {
                "title": "Kel Diva - Haluk Bilginer",
                "venue": "Zorlu PSM",
                "date": "2024-12-15",
                "price": 850.0,
                "description": "Haluk Bilginer ve Zuhal Olcay'ın başrollerinde absürd bir başyapıt",
                "category": "Tiyatro",
            },
            {
                "title": "Kral Lear - Haluk Bilginer",
                "venue": "Zorlu PSM",
                "date": "2024-12-20",
                "price": 950.0,
                "description": "Shakespeare'in ölümsüz eseri Haluk Bilginer yorumuyla",
                "category": "Tiyatro",
            },
            {
                "title": "Don Kişot - Genco Erkal",
                "venue": "Zorlu PSM",
                "date": "2024-12-18",
                "price": 750.0,
                "description": "Genco Erkal'ın tek kişilik oyunu",
                "category": "Tiyatro",
            },
            # Maksim Kültür Merkezi
            {
                "title": "Amadeus",
                "venue": "Maksim Kültür Merkezi",
                "date": "2024-12-22",
                "price": 650.0,
                "description": "Mozart'ın yaşamını anlatan Tony ödüllü oyun",
                "category": "Tiyatro",
            },
            {
                "title": "Bir Delinin Hatıra Defteri",
                "venue": "Maksim Kültür Merkezi",
                "date": "2024-12-25",
                "price": 450.0,
                "description": "Gogol'ün ünlü öyküsünün sahne uyarlaması",
                "category": "Tiyatro",
            },
            # İş Sanat
            {
                "title": "Çok Uzak Fazla Yakın",
                "venue": "İş Sanat",
                "date": "2024-12-16",
                "price": 550.0,
                "description": "İlişkiler üzerine komedi",
                "category": "Tiyatro",
            },
            {
                "title": "Hamlet",
                "venue": "İş Sanat",
                "date": "2024-12-28",
                "price": 600.0,
                "description": "Shakespeare'in en ünlü trajedisi",
                "category": "Tiyatro",
            },
            # Kadıköy Halk Eğitim Merkezi
            {
                "title": "Cehennem Eğlenceleri",
                "venue": "Kadıköy Halk Eğitim Merkezi",
                "date": "2024-12-19",
                "price": 275.0,
                "description": "Daryo Fo'nun absürd komedisi",
                "category": "Tiyatro",
            },
            {
                "title": "Ölü Canlar",
                "venue": "Kadıköy Halk Eğitim Merkezi",
                "date": "2024-12-23",
                "price": 300.0,
                "description": "Gogol'ün satirik romanının sahne uyarlaması",
                "category": "Tiyatro",
            },
            # Bakırköy Belediye Tiyatrosu
            {
                "title": "Şerefe Kadar",
                "venue": "Bakırköy Belediye Tiyatrosu",
                "date": "2024-12-17",
                "price": 225.0,
                "description": "Yerli komedi oyunu",
                "category": "Tiyatro",
            },
            {
                "title": "Yedi Kocalı Hürmüz",
                "venue": "Bakırköy Belediye Tiyatrosu",
                "date": "2024-12-24",
                "price": 250.0,
                "description": "Klasik Türk komedisi",
                "category": "Tiyatro",
            },
            # Müzikaller
            {
                "title": "Biz Bize",
                "venue": "Uniq Hall",
                "date": "2024-12-21",
                "price": 1200.0,
                "description": "Cem Yılmaz müzikali",
                "category": "Müzikal",
            },
            {
                "title": "Evita",
                "venue": "Zorlu PSM",
                "date": "2024-12-26",
                "price": 1450.0,
                "description": "Andrew Lloyd Webber'in ünlü müzikali",
                "category": "Müzikal",
            },
            # Stand-up
            {
                "title": "Cem Yılmaz - Diamond Elite Platinum Plus",
                "venue": "Volkswagen Arena",
                "date": "2024-12-30",
                "price": 875.0,
                "description": "Cem Yılmaz'ın yeni gösterisi",
                "category": "Stand-up",
            },
            {
                "title": "Gökhan Çınar - Yeni Show",
                "venue": "Jolly Joker Vadistanbul",
                "date": "2024-12-27",
                "price": 325.0,
                "description": "Gökhan Çınar stand-up gösterisi",
                "category": "Stand-up",
            },
            # Konserler
            {
                "title": "Sezen Aksu Konseri",
                "venue": "Harbiye Cemil Topuzlu Açıkhava Tiyatrosu",
                "date": "2024-12-29",
                "price": 1650.0,
                "description": "Türk pop müziğinin divası",
                "category": "Konser",
            },
            {
                "title": "Manga Konseri",
                "venue": "İstanbul Kongre Merkezi",
                "date": "2025-01-05",
                "price": 475.0,
                "description": "Manga'nın İstanbul konseri",
                "category": "Konser",
            },
            # Bale & Opera
            {
                "title": "Kuğu Gölü",
                "venue": "Atatürk Kültür Merkezi",
                "date": "2025-01-10",
                "price": 850.0,
                "description": "Çaykovski'nin ünlü balesi",
                "category": "Bale",
            },
            {
                "title": "Carmen",
                "venue": "Atatürk Kültür Merkezi",
                "date": "2025-01-12",
                "price": 750.0,
                "description": "Bizet'nin tutkulu operası",
                "category": "Opera",
            },
            # Çocuk Oyunları
            {
                "title": "Pinokyo",
                "venue": "Caddebostan Kültür Merkezi",
                "date": "2024-12-31",
                "price": 175.0,
                "description": "Çocuklar için klasik masal",
                "category": "Çocuk Oyunu",
            },
            {
                "title": "Kırmızı Başlıklı Kız",
                "venue": "Üsküdar Musiki Cemiyeti",
                "date": "2025-01-06",
                "price": 150.0,
                "description": "İnteraktif çocuk tiyatrosu",
                "category": "Çocuk Oyunu",
            },
        ]

        # Yield each event
        for event_data in demo_events:
            event_item = EventItem(
                title=event_data["title"],
                description=event_data.get("description"),
                venue=event_data["venue"],
                date=event_data["date"],
                price=event_data["price"],
                city="İstanbul",
                category=event_data["category"],
                url=f"https://example.com/event/{event_data['title'].lower().replace(' ', '-')}",
                source="demo",
            )

            self.log_event(event_item)
            yield event_item
