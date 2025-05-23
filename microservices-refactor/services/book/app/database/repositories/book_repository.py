from flask import current_app
from app.database.interfaces.book_repository import BookRepositoryInterface
from app.database.entities.book import Book
from app.settings.extensions import db
from app.utils.image_util import save_image
import os
class BookRepository(BookRepositoryInterface):
    def get_all(self):
        return Book.query.all()

    def get_by_seller_id(self, seller_id: int):
        return Book.query.filter_by(seller_id=seller_id).all()
    
    def get_by_id(self, book_id: int):
        return Book.query.get_or_404(book_id)

    def create(self, title: str, author: str, description: str, price: float, stock: int, seller_id: int, files: dict):
        new_book = Book(title=title, author=author, description=description, price=price, stock=stock, seller_id=seller_id)
        try:
            db.session.add(new_book)
            db.session.flush()

            if 'image' in files:
                image_path = save_image(files['image'], new_book.id)
                if image_path:
                    new_book.image_path = image_path

            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return None
        return new_book

    def update(self, book_id, title: str, author: str, description: str, price: str, stock: int, seller_id: int, files: dict):
        book_to_edit = Book.query.get_or_404(book_id)

        if book_to_edit.seller_id != seller_id:
            return None

        book_to_edit.title = title
        book_to_edit.author = author
        book_to_edit.description = description
        book_to_edit.price = price
        book_to_edit.stock = stock

        try:
            if 'image' in files:
                image_path = save_image(files['image'], book_id)
                if image_path:
                    if book_to_edit.image_path:
                        old_image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], book_to_edit.image_path)
                        if os.path.exists(old_image_path):
                            os.remove(old_image_path)
                    book_to_edit.image_path = image_path

            db.session.commit()
        except Exception as e:
            db.sesison.rollback()
            return None
        return book_to_edit

    def delete(self, book_id: int):
        book_to_delete = Book.query.get_or_404(book_id)

        if book_to_delete.image_path:
            image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], book_to_delete.image_path)
            if os.path.exists(image_path):
                os.remove(image_path)
        try:
            db.session.delete(book_to_delete)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return None
        return book_to_delete
