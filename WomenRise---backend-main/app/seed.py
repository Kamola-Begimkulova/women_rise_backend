"""Seed demo data for WomenRise.

seed_database(db) is idempotent: it returns early if any users already exist.
Creates a realistic dataset matching the pitch — a demo login, sellers,
mentors, courses, marketplace products, community posts, and a few
enrollments — so the UI looks alive on first run.

Demo login:  demo@womenrise.org  /  demo1234
"""
from sqlalchemy.orm import Session

from . import models
from .security import hash_password

U = "https://images.unsplash.com/"


def seed_database(db: Session) -> None:
    if db.query(models.User).count() > 0:
        return

    # ---------- Users ----------
    pw = hash_password("demo1234")
    users = {
        "demo": models.User(
            name="Demo User", email="demo@womenrise.org", password_hash=pw,
            role="learner", bio="Exploring everything WomenRise has to offer.",
            avatar_url=U + "photo-1494790108377-be9c29b29330?w=200&h=200&fit=crop",
        ),
        "amina": models.User(
            name="Amina Yusuf", email="amina@womenrise.org", password_hash=pw,
            role="seller", bio="Founder of Amina Crafts — handwoven textiles from East Africa.",
            expertise="textiles, weaving, small business",
            avatar_url=U + "photo-1573496359142-b8d87734a5a2?w=200&h=200&fit=crop",
        ),
        "lola": models.User(
            name="Lola Karimova", email="lola@womenrise.org", password_hash=pw,
            role="seller", bio="Ceramic artist turning clay into everyday joy.",
            expertise="ceramics, pottery, art",
            avatar_url=U + "photo-1487412720507-e7ab37603c6f?w=200&h=200&fit=crop",
        ),
        "sara": models.User(
            name="Dr. Sara Mensah", email="sara@womenrise.org", password_hash=pw,
            role="mentor", bio="20 years building tech teams. I help women break into engineering and lead with confidence.",
            expertise="software engineering, leadership, career growth",
            avatar_url=U + "photo-1580489944761-15a19d654956?w=200&h=200&fit=crop",
        ),
        "fatima": models.User(
            name="Fatima Noor", email="fatima@womenrise.org", password_hash=pw,
            role="mentor", bio="Serial entrepreneur & investor. Ask me about funding, pricing, and scaling a marketplace business.",
            expertise="entrepreneurship, fundraising, marketing",
            avatar_url=U + "photo-1438761681033-6461ffad8d80?w=200&h=200&fit=crop",
        ),
        "priya": models.User(
            name="Priya Sharma", email="priya@womenrise.org", password_hash=pw,
            role="mentor", bio="Certified wellness coach. Building sustainable habits for busy founders.",
            expertise="wellness, yoga, mindfulness",
            avatar_url=U + "photo-1544005313-94ddf0286df2?w=200&h=200&fit=crop",
        ),
    }
    db.add_all(users.values())
    db.flush()  # assign ids

    # ---------- Courses ----------
    courses = [
        models.Course(title="Python for Absolute Beginners", category="coding", level="Beginner",
            instructor_name="Dr. Sara Mensah", price=0.0, lessons_count=24, duration_hours=8.0, rating=4.9, students_count=1280,
            description="Start coding from zero. Variables, logic, functions, and your first real project — no experience required.",
            image_url=U + "photo-1526379095098-d400fd0bf935?w=800&h=500&fit=crop"),
        models.Course(title="Build Your First Website", category="coding", level="Beginner",
            instructor_name="Dr. Sara Mensah", price=29.0, lessons_count=18, duration_hours=6.5, rating=4.7, students_count=940,
            description="HTML, CSS, and a sprinkle of JavaScript. Ship a portfolio site you're proud of.",
            image_url=U + "photo-1547658719-da2b51169166?w=800&h=500&fit=crop"),
        models.Course(title="Data Analysis with Python", category="coding", level="Intermediate",
            instructor_name="Dr. Sara Mensah", price=49.0, lessons_count=30, duration_hours=12.0, rating=4.8, students_count=610,
            description="Pandas, charts, and real datasets. Turn numbers into decisions.",
            image_url=U + "photo-1551288049-bebda4e38f71?w=800&h=500&fit=crop"),
        models.Course(title="Vinyasa Yoga Foundations", category="yoga", level="Beginner",
            instructor_name="Priya Sharma", price=19.0, lessons_count=20, duration_hours=5.0, rating=4.9, students_count=2100,
            description="Flow, breath, and balance. A calming foundation you can practice anywhere.",
            image_url=U + "photo-1506126613408-eca07ce68773?w=800&h=500&fit=crop"),
        models.Course(title="Morning Mobility & Stretch", category="fitness", level="Beginner",
            instructor_name="Priya Sharma", price=0.0, lessons_count=14, duration_hours=3.0, rating=4.6, students_count=1750,
            description="15-minute routines to wake up your body and protect your joints.",
            image_url=U + "photo-1518611012118-696072aa579a?w=800&h=500&fit=crop"),
        models.Course(title="Strength Training at Home", category="fitness", level="Intermediate",
            instructor_name="Priya Sharma", price=24.0, lessons_count=22, duration_hours=7.0, rating=4.7, students_count=830,
            description="Build real strength with minimal equipment and smart programming.",
            image_url=U + "photo-1571019613454-1cb2f99b2d8b?w=800&h=500&fit=crop"),
        models.Course(title="Start & Grow Your Small Business", category="business", level="Beginner",
            instructor_name="Fatima Noor", price=39.0, lessons_count=26, duration_hours=10.0, rating=4.9, students_count=1340,
            description="From idea to first sale: validation, pricing, branding, and launch.",
            image_url=U + "photo-1556761175-5973dc0f32e7?w=800&h=500&fit=crop"),
        models.Course(title="Marketing for Makers", category="business", level="Intermediate",
            instructor_name="Fatima Noor", price=45.0, lessons_count=21, duration_hours=8.5, rating=4.8, students_count=720,
            description="Find your customers and tell your story — social, email, and content that sells.",
            image_url=U + "photo-1460925895917-afdab827c52f?w=800&h=500&fit=crop"),
    ]
    db.add_all(courses)

    # ---------- Products ----------
    products = [
        models.Product(seller_id=users["amina"].id, title="Handwoven Wool Scarf", category="textiles", price=48.0, stock=12, rating=4.9,
            description="Naturally dyed, handwoven on a traditional loom. Soft, warm, one of a kind.",
            image_url=U + "photo-1601924994987-69e26d50dc26?w=800&h=600&fit=crop"),
        models.Product(seller_id=users["amina"].id, title="Embroidered Table Runner", category="textiles", price=36.0, stock=8, rating=4.8,
            description="Hand-embroidered cotton runner with geometric motifs.",
            image_url=U + "photo-1513519245088-0e12902e35ca?w=800&h=600&fit=crop"),
        models.Product(seller_id=users["lola"].id, title="Stoneware Mug Set (2)", category="home", price=42.0, stock=15, rating=5.0,
            description="A pair of wheel-thrown mugs glazed in soft sage. Microwave & dishwasher safe.",
            image_url=U + "photo-1514228742587-6b1558fcca3d?w=800&h=600&fit=crop"),
        models.Product(seller_id=users["lola"].id, title="Ceramic Planter — Speckled", category="home", price=28.0, stock=20, rating=4.7,
            description="Hand-glazed planter with drainage. Perfect for herbs and succulents.",
            image_url=U + "photo-1485955900006-10f4d324d411?w=800&h=600&fit=crop"),
        models.Product(seller_id=users["amina"].id, title="Beaded Statement Necklace", category="jewelry", price=34.0, stock=10, rating=4.8,
            description="Glass beads strung by hand. Bold color, lightweight feel.",
            image_url=U + "photo-1599643478518-a784e5dc4c8f?w=800&h=600&fit=crop"),
        models.Product(seller_id=users["lola"].id, title="Brass Hoop Earrings", category="jewelry", price=22.0, stock=25, rating=4.6,
            description="Minimalist hammered hoops, hypoallergenic posts.",
            image_url=U + "photo-1535632066927-ab7c9ab60908?w=800&h=600&fit=crop"),
        models.Product(seller_id=users["lola"].id, title="Abstract Canvas — 'Sunrise'", category="art", price=120.0, stock=3, rating=5.0,
            description="Original acrylic on canvas, 40x50cm. Signed by the artist.",
            image_url=U + "photo-1547891654-e66ed7ebb968?w=800&h=600&fit=crop"),
        models.Product(seller_id=users["amina"].id, title="Botanical Print Set (3)", category="art", price=30.0, stock=18, rating=4.7,
            description="Giclée prints of original botanical illustrations. Frame not included.",
            image_url=U + "photo-1502082553048-f009c37129b9?w=800&h=600&fit=crop"),
        models.Product(seller_id=users["lola"].id, title="Whipped Shea Body Butter", category="beauty", price=18.0, stock=30, rating=4.9,
            description="Small-batch, unscented, made with raw shea and jojoba oil.",
            image_url=U + "photo-1556228720-195a672e8a03?w=800&h=600&fit=crop"),
    ]
    db.add_all(products)

    # ---------- Community posts ----------
    posts = [
        models.Post(author_id=users["amina"].id, category="wins", likes=42,
            title="My scarves sold out in the first week! 🎉",
            body="I almost didn't list them. Thank you to everyone in this community who pushed me to start. The Marketing for Makers course changed how I write my product descriptions."),
        models.Post(author_id=users["demo"].id, category="questions", likes=7,
            title="Best course to learn coding from zero?",
            body="I have no technical background but want to build a simple site for my shop. Where should I start?"),
        models.Post(author_id=users["lola"].id, category="collab", likes=15,
            title="Looking for a photographer to swap services",
            body="I make ceramics, I'll trade a mug set for product photos. Anyone in the community do photography?"),
        models.Post(author_id=users["fatima"].id, category="general", likes=58,
            title="Pricing tip: you're probably undercharging",
            body="A pattern I see constantly with makers: pricing only for materials and forgetting your time. Your hours have value. Price for sustainability, not just survival."),
        models.Post(author_id=users["priya"].id, category="wins", likes=23,
            title="30 days of morning mobility — done!",
            body="Started the free Morning Mobility course and stuck with it. My back pain is noticeably better. Small habits, big change."),
    ]
    db.add_all(posts)
    db.flush()

    # ---------- Comments ----------
    db.add_all([
        models.Comment(post_id=posts[0].id, author_id=users["fatima"].id, body="So proud of you! This is just the beginning. 💜"),
        models.Comment(post_id=posts[0].id, author_id=users["demo"].id, body="Congrats! Your work is gorgeous."),
        models.Comment(post_id=posts[1].id, author_id=users["sara"].id, body="Start with 'Python for Absolute Beginners' (it's free), then 'Build Your First Website'."),
        models.Comment(post_id=posts[3].id, author_id=users["amina"].id, body="This hit hard. Raising my prices today."),
    ])

    # ---------- Enrollments for demo user ----------
    db.add_all([
        models.Enrollment(user_id=users["demo"].id, course_id=courses[0].id, progress=60),
        models.Enrollment(user_id=users["demo"].id, course_id=courses[3].id, progress=100, completed=True),
        models.Enrollment(user_id=users["demo"].id, course_id=courses[6].id, progress=20),
    ])

    db.commit()
