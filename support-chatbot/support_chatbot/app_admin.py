import streamlit as st
import sqlite3


st.title("Admin Dashboard")


email = st.text_input("Admin email")
password = st.text_input(
    "Password",
    type="password"
)


if st.button("Login"):

    if email and password:

        st.session_state.admin=True


if st.session_state.get("admin"):

    conn=sqlite3.connect(
        "ecommerce.db"
    )

    rows=conn.execute(
        """
        SELECT
        id,
        user_email,
        action_type,
        order_id,
        thread_id,
        status
        FROM pending_actions
        WHERE status='PENDING'
        """
    ).fetchall()


    for row in rows:

        st.write(row)

        col1,col2=st.columns(2)

        if col1.button(
            "Approve",
            key=f"a{row[0]}"
        ):
            st.success("Approved")


        if col2.button(
            "Reject",
            key=f"r{row[0]}"
        ):
            st.warning("Rejected")