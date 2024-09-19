import os
import streamlit as st
import camelot as cam
import pandas as pd
import base64
import chardet
import io

# Display the logo
logo_path = os.path.join(os.path.dirname(__file__), 'jcmz_logo.jfif')
st.image(logo_path)

# Main title for the Streamlit app
st.title("JCMZ PDF to CSV Conversion Software")
st.subheader("The Art of Business Science")

# File uploader on Streamlit for PDF files
input_pdf = st.file_uploader(label="Upload your PDF here", type="pdf")

# Option to process all pages into one continuous CSV
continuous_csv = st.checkbox("Convert all pages into one continuous CSV")

# Option to extract a specific page number
st.markdown("## Page Number")
page_number = st.text_input("Enter the page # from where you want to extract the PDF, e.g., 3", value="1")

# Run this block only when a PDF is uploaded
if input_pdf is not None:
    # Save uploaded PDF to a file
    with open("input.pdf", "wb") as f:
        f.write(input_pdf.read())

    try:
        if continuous_csv:
            st.markdown("### Processing all pages for continuous CSV")
            all_tables = []

            # Extract tables from all pages
            tables = cam.read_pdf("input.pdf", pages="all", flavor="stream")
            for page in tables:
                all_tables.append(page.df)

            if all_tables:
                combined_df = pd.concat(all_tables, ignore_index=True)
                st.markdown("### Continuous Output Table")
                st.dataframe(combined_df)

                # Create a buffer for CSV download
                csv_buffer = io.StringIO()

                # Detect encoding and convert to UTF-8
                raw_data = combined_df.to_csv(index=False).encode()
                result = chardet.detect(raw_data)
                charenc = result['encoding']

                combined_df.to_csv(csv_buffer, index=False, encoding="utf-8")

                # Download button for the continuous CSV
                st.download_button(
                    label="Download Continuous CSV",
                    data=csv_buffer.getvalue(),
                    file_name="continuous_output.csv",
                    mime="text/csv"
                )
            else:
                st.write("No tables found in the PDF.")

        else:
            st.markdown(f"### Extracting tables from page {page_number}")

            # Extract tables from the specified page
            tables = cam.read_pdf("input.pdf", pages=page_number, flavor="stream")
            if len(tables) > 0:
                st.markdown("### Number of Tables")
                st.write(f"Found {len(tables)} table(s) on page {page_number}")

                # Select a table to display
                table_option = st.selectbox("Select the table to display", options=range(len(tables)))

                # Display the selected table
                selected_table = tables[table_option].df
                st.markdown("### Output Table")
                st.dataframe(selected_table)

                # Download button for the selected table
                csv_buffer = io.StringIO()
                selected_table.to_csv(csv_buffer, index=False, encoding="utf-8")

                st.download_button(
                    label="Download CSV File",
                    data=csv_buffer.getvalue(),
                    file_name=f"output_table_page{page_number}_table{table_option+1}.csv",
                    mime="text/csv"
                )
            else:
                st.write(f"No tables found on page {page_number}.")

    except Exception as e:
        st.error(f"Error processing the PDF: {e}")

