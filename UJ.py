import streamlit as st
import pandas as pd
from io import BytesIO


st.set_page_config(
    page_title="Generator Template Approval Uang Jalan",
    page_icon="💰",
    layout="wide",
)


# ============================================================
# LOGIC ASLI — dipertahankan
# ============================================================

DEFAULT_MAPPINGS = {
    "driver": [
        "KORLAP",
        "NAMA KORLAP",
        "DRIVER",
        "NAMA DRIVER",
    ],
    "uang_jalan": [
        "UANG JALAN DRIVER",
        "UANG JALAN",
        "BIAYA JALAN",
        "HARGA TAGIHAN",
    ],
    "no_uj": [
        "NO.UJ ODOO",
        "NO UJ",
        "NO_UJ",
        "NO UJ ODOO",
    ],
    "customer": [
        "CUSTOMER SS",
        "CUSTOMER_SS",
        "AGREEMENT",
        "CUSTOMER",
        "PT",
        "NAMA CUSTOMER",
        "CUSTOMER NAME",
    ],
    "tipe": [
        "TYPE DISTRIBUSI UNIT",
        "TIPE DISTRIBUSI",
        "TIPE",
        "JENIS",
        "TARIK/KIRIM",
    ],
    "asal": [
        "AREA ASAL/PICK UP",
        "ASAL",
        "ORIGIN",
        "AREA ASAL",
    ],
    "tujuan": [
        "TUJUAN",
        "DESTINATION",
        "AREA TUJUAN",
    ],
}


FIELD_LABELS = [
    ("Nama (Ambil dari Korlap)", "driver"),
    ("Uang Jalan (Rp)", "uang_jalan"),
    ("No. UJ Odoo (Kunci Grouping)", "no_uj"),
    ("Customer Name (PT)", "customer"),
    ("Tipe (Tarik/Kirim)", "tipe"),
    ("Asal (Origin)", "asal"),
    ("Tujuan (Destination)", "tujuan"),
]


def format_rupiah(amount):
    try:
        formatted = f"{int(amount):,}".replace(",", ".")
        return f"Rp. {formatted}"
    except Exception:
        return "Rp. 0"


def detect_column(columns, mapping):
    columns_upper = [str(col).upper() for col in columns]

    for keyword in mapping:
        keyword_upper = keyword.upper()

        if keyword_upper in columns_upper:
            idx = columns_upper.index(keyword_upper)
            return columns[idx]

    return None


def generate_text(
    df,
    col_driver,
    col_uang_jalan,
    col_no_uj,
    col_customer,
    col_tipe,
    col_asal,
    col_tujuan,
):
    # Logika pemrosesan dibuat sama seperti aplikasi asli.
    df_filtered = df.dropna(subset=[col_no_uj]).copy()

    df_filtered[col_uang_jalan] = pd.to_numeric(
        df_filtered[col_uang_jalan],
        errors="coerce",
    ).fillna(0)

    hasil = (
        "Dear Pak Jeffrey,\n"
        "Mohon bantuannya untuk approval pengajuan sbb :\n\n"
    )

    grouped = df_filtered.groupby(col_no_uj)
    idx = 1

    for no_uj, group in grouped:
        nama_driver = str(
            group[col_driver].iloc[0]
        ).strip()

        if nama_driver.lower() in (
            "nan",
            "none",
            "",
            "nat",
        ):
            nama_driver = "-"

        nama_customer = str(
            group[col_customer].iloc[0]
        ).strip()

        if nama_customer.lower() in (
            "nan",
            "none",
            "",
            "nat",
        ):
            nama_customer = ""

        jumlah_do = len(group)
        total_uang = group[col_uang_jalan].sum()
        str_uang = format_rupiah(total_uang)

        rute_list = []

        for _, row in group.iterrows():
            tipe = str(row[col_tipe]).strip()
            if tipe.lower() == "nan":
                tipe = ""

            asal = str(row[col_asal]).strip()
            if asal.lower() == "nan":
                asal = ""

            tujuan = str(row[col_tujuan]).strip()
            if tujuan.lower() == "nan":
                tujuan = ""

            rute_list.append(
                f"{tipe} ({asal} - {tujuan})".strip()
            )

        rute_gabungan = ", ".join(rute_list)

        line = (
            f"{idx}. {nama_driver} "
            f"{jumlah_do} DO "
            f"{str_uang} "
            f"{no_uj} "
            f"{nama_customer} "
            f"{rute_gabungan}\n"
        )

        hasil += line
        idx += 1

    hasil += (
        "\nDear mba Vani dan tim finance, "
        "mohon dibantu proses uang jalannya ya.\n\n"
        "Demikian, terimakasih"
    )

    return hasil


# ============================================================
# STREAMLIT UI — hanya menggantikan Tkinter
# ============================================================

st.title("Generator Template Approval Uang Jalan")
st.caption("Versi Streamlit dari aplikasi UANG JALAN")

uploaded_file = st.file_uploader(
    "Load File (Excel/CSV)",
    type=["xlsx", "xls", "csv"],
)

if uploaded_file is not None:
    try:
        if uploaded_file.name.lower().endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        columns = list(df.columns)

        st.success(
            f"File berhasil dimuat: **{uploaded_file.name}**"
        )

        st.subheader(
            "Mapping Header "
            "(Otomatis mendeteksi kolom yang sesuai)"
        )

        selected = {}

        for label_text, var_name in FIELD_LABELS:
            detected = detect_column(
                columns,
                DEFAULT_MAPPINGS[var_name],
            )

            options = [""] + columns

            default_index = 0
            if detected in columns:
                default_index = columns.index(detected) + 1

            selected[var_name] = st.selectbox(
                label_text,
                options=options,
                index=default_index,
                key=f"mapping_{var_name}",
            )

        st.divider()

        if st.button(
            "Generate Text",
            type="primary",
            use_container_width=True,
        ):
            all_mapped = all(
                selected[var_name]
                for _, var_name in FIELD_LABELS
            )

            if not all_mapped:
                st.warning(
                    "Harap pastikan semua mapping kolom sudah terisi!"
                )
            else:
                try:
                    hasil = generate_text(
                        df=df,
                        col_driver=selected["driver"],
                        col_uang_jalan=selected["uang_jalan"],
                        col_no_uj=selected["no_uj"],
                        col_customer=selected["customer"],
                        col_tipe=selected["tipe"],
                        col_asal=selected["asal"],
                        col_tujuan=selected["tujuan"],
                    )

                    st.session_state["hasil_text"] = hasil

                except Exception as e:
                    st.error(
                        "Terjadi kesalahan saat memproses data:"
                    )
                    st.exception(e)

        if "hasil_text" in st.session_state:
            st.subheader("Hasil Template")

            hasil = st.session_state["hasil_text"]

            st.text_area(
                "Teks hasil — bisa langsung dicopy",
                value=hasil,
                height=500,
                label_visibility="collapsed",
            )

            st.download_button(
                label="Download Hasil sebagai TXT",
                data=hasil,
                file_name="hasil_approval_uang_jalan.txt",
                mime="text/plain",
                use_container_width=True,
            )

    except Exception as e:
        st.error("Gagal membaca file.")
        st.exception(e)
else:
    st.info(
        "Silakan upload file Excel atau CSV untuk memulai."
    )
