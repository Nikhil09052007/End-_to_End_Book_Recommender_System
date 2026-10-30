import os
import sys
import pickle
import streamlit as st
import numpy as np
from books_recommender_system.logger.log import logging
from books_recommender_system.config.configuration import AppConfiguration
from books_recommender_system.pipeline.training_pipeline import TrainingPipeline
from books_recommender_system.exception.exception_handler import AppException


class Recommendation:
    def __init__(self,app_config = AppConfiguration()):
        try:
            self.recommendation_config= app_config.get_recommendation_config()
        except Exception as e:
            raise AppException(e, sys) from e


    def fetch_poster(self,suggestion):
        try:
            poster_url = []
            final_rating = pickle.load(
                open(self.recommendation_config.final_rating_serialized_objects, 'rb')
            )
            book_pivot = pickle.load(
                open(self.recommendation_config.book_pivot_serialized_objects, 'rb')
            )

            for book_id in suggestion[0]:
                title = book_pivot.index[book_id]
                matches = final_rating.loc[final_rating['title'] == title, 'image_url']
                poster_url.append(matches.iloc[0] if not matches.empty else None)

            return poster_url
        
        except Exception as e:
            raise AppException(e, sys) from e
        


    def recommend_book(self,book_name):
        try:
            books_list = []
            model = pickle.load(open(self.recommendation_config.trained_model_path,'rb'))
            book_pivot =  pickle.load(open(self.recommendation_config.book_pivot_serialized_objects,'rb'))
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
            st.text("Training Completed!")
            logging.info(f"Recommended successfully!")
        except Exception as e:
            raise AppException(e, sys) from e

    
    def recommendations_engine(self,selected_books):
        try:
            recommended_books,poster_url = self.recommend_book(selected_books)
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.text(recommended_books[1])
                if poster_url[1]:
                    st.image(poster_url[1])
            with col2:
                st.text(recommended_books[2])
                if poster_url[2]:
                    st.image(poster_url[2])

            with col3:
                st.text(recommended_books[3])
                if poster_url[3]:
                    st.image(poster_url[3])
            with col4:
                st.text(recommended_books[4])
                if poster_url[4]:
                    st.image(poster_url[4])
            with col5:
                st.text(recommended_books[5])
                if poster_url[5]:
                    st.image(poster_url[5])
        except Exception as e:
            raise AppException(e, sys) from e



if __name__ == "__main__":
    st.header('End to End Books Recommender System')
    st.text("This is a collaborative filtering based recommendation system!")

    obj = Recommendation()

    #Training
    if st.button('Train Recommender System'):
        obj.train_engine()

    book_names = pickle.load(open(os.path.join('templates','book_names.pkl') ,'rb'))
    selected_books = st.selectbox(
        "Type or select a book from the dropdown",
        book_names)
    
    #recommendation
    if st.button('Show Recommendation'):
        if not os.path.isfile(obj.recommendation_config.trained_model_path):
            st.error('The recommender model has not been trained yet. Click “Train Recommender System” first, then try again.')
        else:
            obj.recommendations_engine(selected_books)

