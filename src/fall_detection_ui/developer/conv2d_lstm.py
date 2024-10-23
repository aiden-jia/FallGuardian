import streamlit as st

import tensorflow as tf

model = tf.keras.models.load_model('../model/LRCN_FAIL_Date_Time_2024_08_20__00_12_41__Loss_0.6136224865913391__Accuracy_0.8586956262588501.h5')
#model.summary()
model.summary(print_fn=lambda x: st.text(x))

# Visualize Keras Model With st.graphviz_chart   https://github.com/streamlit/streamlit/issues/341
model_graph = tf.keras.utils.model_to_dot(model)
model_graph = str(model_graph)
st.graphviz_chart(model_graph)