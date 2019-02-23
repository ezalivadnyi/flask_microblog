from application.models import Post, User
from application import db
from mimesis import Generic


def generate_post(author, count=10, locale='en'):
    generic = Generic(locale)
    for _ in range(count):
        post = Post(
            title=generic.text.text(1)[0:60],
            body=generic.text.text(50),
            author=author
        )
        print(post)
        db.session.add(post)
        try:
            db.session.commit()
        except:
            db.session.rollback()


def generate_user(count=10, locale='en'):
    for _ in range(count):
        generic = Generic(locale)
        user = User(
            username=generic.person.username(),
            email=generic.person.email()
        )
        user.set_password(generic.person.password())
        db.session.add(user)
        try:
            db.session.commit()
        except:
            db.session.rollback()
        generate_post(author=user)


if __name__ == '__main__':
    generate_user()
