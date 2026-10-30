import os
import sys
import pickle
import streamlit as st
import numpy as np
from books_recommender_system.logger.log import logging
from books_recommender_system.config.configuration import AppConfiguration
from books_recommender_system.pipeline.training_pipeline import TrainingPipeline
from books_recommender_system.exception.exception_handler import AppException


@st.cache_resource(max_entries=2)
def load_model(path, modified_at):
    with open(path, 'rb') as model_file:
        return pickle.load(model_file)


@st.cache_data(max_entries=4)
def load_pickle_data(path, modified_at):
    with open(path, 'rb') as data_file:
        return pickle.load(data_file)


class Recommendation:
    def __init__(self,app_config = AppConfiguration()):
        try:
            self.recommendation_config= app_config.get_recommendation_config()
        except Exception as e:
            raise AppException(e, sys) from e


    def fetch_poster(self,suggestion):
        try:
            poster_url = []
            final_rating_path = self.recommendation_config.final_rating_serialized_objects
            book_pivot_path = self.recommendation_config.book_pivot_serialized_objects
            final_rating = load_pickle_data(
                final_rating_path, os.stat(final_rating_path).st_mtime_ns
            )
            book_pivot = load_pickle_data(
                book_pivot_path, os.stat(book_pivot_path).st_mtime_ns
            )

            for book_id in suggestion[0]:
                title = book_pivot.index[book_id]
                matches = final_rating.loc[final_rating['title'] == title, 'image_url']
                url = matches.iloc[0] if not matches.empty else None
                poster_url.append(url if isinstance(url, str) and url.startswith('http') else None)

            return poster_url
        
        except Exception as e:
            raise AppException(e, sys) from e
        


    def recommend_book(self,book_name):
        try:
            model_path = self.recommendation_config.trained_model_path
            book_pivot_path = self.recommendation_config.book_pivot_serialized_objects
            model = load_model(model_path, os.stat(model_path).st_mtime_ns)
            book_pivot = load_pickle_data(
                book_pivot_path, os.stat(book_pivot_path).st_mtime_ns
            )
            book_id = np.where(book_pivot.index == book_name)[0][0]
            _, suggestion = model.kneighbors(
                book_pivot.iloc[book_id, :].values.reshape(1, -1), n_neighbors=6
            )

            poster_url = self.fetch_poster(suggestion)
            
            books_list = book_pivot.index[suggestion[0]].tolist()
            return books_list , poster_url   
        
        except Exception as e:
            raise AppException(e, sys) from e


    def train_engine(self):
        try:
            obj = TrainingPipeline()
            obj.start_training_pipeline()
            st.success("Training completed!")
            logging.info("Recommender training completed successfully.")
        except Exception as e:
            raise AppException(e, sys) from e

    
    def recommendations_engine(self,selected_books):
        try:
            recommended_books,poster_url = self.recommend_book(selected_books)
            columns = st.columns(5)
            for column, title, image_url in zip(
                columns, recommended_books[1:], poster_url[1:]
            ):
                with column:
                    st.write(title)
                    if image_url:
                        st.image(image_url, alt=f"Cover of {title}", width="stretch")
        except Exception as e:
            raise AppException(e, sys) from e



if __name__ == "__main__":
    st.set_page_config(page_title="Book recommender", layout="wide")
    st.title("Book recommender")
    st.caption("Discover books with rating patterns similar to a title you like.")

    obj = Recommendation()

    with st.expander("Training options"):
        st.caption(
            "Training downloads the source dataset and may take several minutes. "
            "The checked-in model is ready to use without retraining."
        )
        if st.button("Train or refresh the recommender"):
            with st.spinner("Downloading data and training the recommender..."):
                obj.train_engine()

    book_names_path = os.path.join('templates', 'book_names.pkl')
    with open(book_names_path, 'rb') as book_names_file:
        book_names = pickle.load(book_names_file)
    selected_books = st.selectbox(
        "Type or select a book from the dropdown",
        book_names)
    
    #recommendation
    if st.button('Show Recommendation'):
        required_files = (
            obj.recommendation_config.trained_model_path,
            obj.recommendation_config.book_pivot_serialized_objects,
            obj.recommendation_config.final_rating_serialized_objects,
        )
        missing_files = [path for path in required_files if not os.path.isfile(path)]
        if missing_files:
            st.error(
                "The recommender files are missing. Use the training option above "
                "to generate them, then try again."
            )
        else:
            obj.recommendations_engine(selected_books)

