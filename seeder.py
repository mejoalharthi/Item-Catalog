from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from catalog_setup import Base, User, Category, Item

engine = create_engine('sqlite:///catalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# Users
User01 = User(name="Amjad Alharthi", email="amjad.12336@gmail.com")
session.add(User01)
session.commit()


# Drinks categories:

# Specialized coffee
Category01 = Category(name="Specialized coffee")

session.add(Category01)
session.commit()

Item01_1 = Item(name="Espresso", item_info="""A strong concentration
                      of black coffee made in an espresso machine
                      by forcing steam through pressurized coffee beans.
                      This drink contains no milk.""",
                user_id=1, category=Category01)
session.add(Item01_1)
session.commit()

Item02_1 = Item(name="Cortado",
                item_info="Equal parts espresso and steamed milk.",
                user_id=1, category=Category01)
session.add(Item02_1)
session.commit()

Item03_1 = Item(name="Americano",
                item_info="""A single shot of espresso
                        added to a cup of hot water.""",
                user_id=1, category=Category01)
session.add(Item03_1)
session.commit()

Item04_1 = Item(name="Cafe Mocha", item_info="""Two thirds steamed milk,
                one part espresso, and one part chocolate
                syrup or powder.""",
                user_id=1, category=Category01)
session.add(Item04_1)
session.commit()

Item05_1 = Item(name="Cappuccino", item_info="""Three equal parts of steamed
                    milk,foamed milk, and espresso.You can add
                    flavoring syrups to make vanilla,caramel,
                    or hazelnut cappuccinos.""",
                user_id=1, category=Category01)
session.add(Item05_1)
session.commit()

Item06_1 = Item(name="Cafe Latte",
                item_info="""One part espresso with three parts steamed
                 milk with froth on top.""",
                user_id=1, category=Category01)
session.add(Item06_1)
session.commit()

Item07_1 = Item(name="Macchiato",
                item_info="""Espresso with a dollop of steamed milk added
                in a 4:1 ratio.""",
                user_id=1, category=Category01)
session.add(Item07_1)
session.commit()


# Coffee Brewing
Category02 = Category(name="Coffee Brewing")

session.add(Category02)
session.commit()

Item01_2 = Item(name="French Press", item_info="""This simple brewing
                    method steeps coffee grounds in
                    hot water and then presses the grounds out.
                    You can find a French press at most grocery stores,
                    coffee shops or home appliance stores.""",
                user_id=1, category=Category02)
session.add(Item01_2)
session.commit()

Item02_2 = Item(name="Automatic Drip Coffee", item_info="""High in caffeine and
                    convenience,he automatic drip coffee
                    maker is the most common brewing method.""",
                user_id=1, category=Category02)
session.add(Item02_2)
session.commit()

Item03_2 = Item(name="Pour Over Coffee", item_info="""Chemex and Hario are
                    common pour over coffee makers,
                    yielding a strong, full bodied cup of coffee""",
                user_id=1, category=Category02)
session.add(Item03_2)
session.commit()

Item04_2 = Item(name="Cold Brew Coffee", item_info="""Cold brew is steeped in
                    the fridge for a day,
                    making for a less acidic glass of iced coffee.""",
                user_id=1, category=Category02)
session.add(Item04_2)
session.commit()


# Iced Coffee Drinks
Category03 = Category(name="Iced Coffee")

session.add(Category03)
session.commit()

Item01_3 = Item(name="Cafe Affogato", item_info="""simply put, is ice cream
                    with a shot of espresso poured over it.""",
                user_id=1, category=Category03)
session.add(Item01_3)
session.commit()

Item02_3 = Item(name="Iced Americanos", item_info="""Shot of espresso going
                    directly onto the ice and then topped with iced water.""",
                user_id=1, category=Category03)
session.add(Item02_3)
session.commit()


# Frappuccinos

Category04 = Category(name="Frappuccinos")

session.add(Category04)
session.commit()

Item01_4 = Item(name="Caramel Frappuccino", item_info="""Buttery caramel syrup
                    meets coffee, milk and ice for a rendezvous in the blender.
                    Then whipped cream and caramel sauce layer the love on
                    top.""",
                user_id=1, category=Category04)
session.add(Item01_4)
session.commit()

Item01_4 = Item(name="Double Chocolaty Chip Creme Frappuccino",
                item_info="""Rich mocha flavored sauce meets up with chocolaty
                chips, milk and ice for a blender bash. Top it off with
                sweetened whipped cream and mocha drizzle for a real party
                in your mouth.""",
                user_id=1, category=Category04)
session.add(Item01_4)
session.commit()


print "added menu items!"
