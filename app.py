import numpy as np
import streamlit as st
from PIL import Image, ImageEnhance, ImageOps
from rembg import remove
from streamlit_cropper import st_cropper

VERSION = "0.6.1"

st.set_page_config(
    page_title="ĐỒ ÁN XỬ LÝ ẢNH",
    page_icon="🖼️",
    layout="wide",
)

# ---------- SIDEBAR ----------
with open("sidebar.html", "r", encoding="UTF-8") as sidebar_file:
    sidebar_html = sidebar_file.read().replace("{VERSION}", VERSION)

with st.sidebar:
    st.components.v1.html(sidebar_html, height=750)

# ---------- HEADER ----------
st.title("🖼️ ĐỒ ÁN XỬ LÝ ẢNH")

# ---------- FUNCTIONS ----------
def _reset(key: str) -> None:
    if key == "all":
        st.session_state["rotate_slider"] = 0
        st.session_state["brightness_slider"] = st.session_state[
            "saturation_slider"
        ] = st.session_state["contrast_slider"] = 100
        st.session_state["bg"] = st.session_state["crop"] = st.session_state[
            "mirror"
        ] = st.session_state["gray_bw"] = 0
    elif key == "rotate_slider":
        st.session_state["rotate_slider"] = 0
    elif key == "checkboxes":
        st.session_state["crop"] = st.session_state["mirror"] = st.session_state[
            "gray_bw"
        ] = 0
    else:
        st.session_state[key] = 100


def _randomize() -> None:
    st.session_state["mirror"] = np.random.choice([0, 1])
    st.session_state["rotate_slider"] = np.random.randint(0, 360)
    st.session_state["brightness_slider"] = np.random.randint(0, 200)
    st.session_state["saturation_slider"] = np.random.randint(0, 200)
    st.session_state["contrast_slider"] = np.random.randint(0, 200)
    st.session_state["sharpness_slider"] = np.random.randint(0, 200)


# ---------- OPERATIONS ----------
option = st.radio(
    label="Tải lên một ảnh hoặc chụp bằng máy ảnh của bạn",
    options=("Tải lên một ảnh ⬆️","Chụp bằng máy ảnh của bạn"),
)

if option == "Chụp bằng máy ảnh của bạn":
    upload_img = st.camera_input(
        label="Chụp ảnh bằng camera",
    )
else:
    upload_img = st.file_uploader(
        label="Tải lên một ảnh",
        type=["bmp", "jpg", "jpeg", "png", "svg"],
    )

if upload_img is not None:
    name = upload_img.name.rsplit(".", 1)[0]
    ext = upload_img.name.split(".")[-1]
    pil_img = Image.open(upload_img).convert("RGB")
    img_arr = np.asarray(pil_img)

    # ---------- PROPERTIES ----------
    st.image(img_arr, use_column_width="auto", caption="Uploaded Image")
    st.text(f"Original width = {pil_img.size[0]}px and height = {pil_img.size[1]}px")

    st.caption("All changes are applied on top of the previous change.")

    # ---------- CROP ----------
    st.text("Crop image ✂️")
    cropped_img = st_cropper(Image.fromarray(img_arr), should_resize_image=True)
    st.text(
        f"Cropped width = {cropped_img.size[0]}px and height = {cropped_img.size[1]}px"
    )

    with st.container():
        lcol, rcol = st.columns(2)
        if lcol.checkbox(
            label="Use cropped Image?",
            help="Select to use the cropped image in further operations",
            key="crop",
        ):
            image = cropped_img
        else:
            image = Image.fromarray(img_arr)

        # ---------- REMOVE BACKGROUND ----------
        if lcol.checkbox(
            label="Remove background?",
            help="Select to remove background from the image",
            key="bg",
        ):
            image = remove(image)

        # ---------- MIRROR ----------
        if lcol.checkbox(
            label="Mirror image? 🪞",
            help="Select to mirror the image",
            key="mirror",
        ):
            image = ImageOps.mirror(image)

        # ---------- GRAYSCALE / B&W ----------
        flag = True

        if lcol.checkbox(
            "Convert to grayscale / black & white? 🔲",
            key="gray_bw",
            help="Select to convert image to grayscale or black and white",
        ):
            mode = "L"
            if (
                lcol.radio(
                    label="Grayscale or B&W",
                    options=("Grayscale", "Black & White"),
                )
                == "Grayscale"
            ):
                image = image.convert(mode)
            else:
                flag = False
                lcol.warning(
                    "Some operations not available for black and white images."
                )
                thresh = np.array(image).mean()
                fn = lambda x: 255 if x > thresh else 0
                image = image.convert(mode).point(fn, mode="1")
        else:
            mode = "RGB"
        rcol.image(
            image,
            use_column_width="auto",
        )

        if lcol.button(
            "↩️ Reset",
            on_click=_reset,
            use_container_width=True,
            kwargs={"key": "checkboxes"},
        ):
            lcol.success("Image reset to original!")

    st.markdown("""---""")

    # ---------- OTHER OPERATIONS ----------
    # ---------- 1ST ROW ----------
    with st.container():
        lcol, mcol, rcol = st.columns(3)

        # ---------- ROTATE ----------
        if "rotate_slider" not in st.session_state:
            st.session_state["rotate_slider"] = 0
        degrees = lcol.slider(
            "Drag slider to rotate image clockwise 🔁",
            min_value=0,
            max_value=360,
            value=st.session_state["rotate_slider"],
            key="rotate_slider",
        )
        rotated_img = image.rotate(360 - degrees)
        lcol.image(
            rotated_img,
            use_column_width="auto",
            caption=f"Rotated by {degrees} degrees clockwise",
        )
        if lcol.button(
            "↩️ Reset Rotation",
            on_click=_reset,
            use_container_width=True,
            kwargs={"key": "rotate_slider"},
        ):
            lcol.success("Rotation reset to original!")

        if flag:
            # ---------- BRIGHTNESS ----------
            if "brightness_slider" not in st.session_state:
                st.session_state["brightness_slider"] = 100
            brightness_factor = mcol.slider(
                "Drag slider to change brightness 💡",
                min_value=0,
                max_value=200,
                value=st.session_state["brightness_slider"],
                key="brightness_slider",
            )
            brightness_img = np.asarray(
                ImageEnhance.Brightness(rotated_img).enhance(brightness_factor / 100)
            )
            mcol.image(
                brightness_img,
                use_column_width="auto",
                caption=f"Brightness: {brightness_factor}%",
            )
            if mcol.button(
                "↩️ Reset Brightness",
                on_click=_reset,
                use_container_width=True,
                kwargs={"key": "brightness_slider"},
            ):
                mcol.success("Brightness reset to original!")

            # ---------- SATURATION ----------
            if "saturation_slider" not in st.session_state:
                st.session_state["saturation_slider"] = 100
            saturation_factor = rcol.slider(
                "Drag slider to change saturation",
                min_value=0,
                max_value=200,
                value=st.session_state["saturation_slider"],
                key="saturation_slider",
            )
            saturation_img = np.asarray(
                ImageEnhance.Color(Image.fromarray(brightness_img)).enhance(
                    saturation_factor / 100
                )
            )
            rcol.image(
                saturation_img,
                use_column_width="auto",
                caption=f"Saturation: {saturation_factor}%",
            )
            if rcol.button(
                "↩️ Reset Saturation",
                on_click=_reset,
                use_container_width=True,
                kwargs={"key": "saturation_slider"},
            ):
                rcol.success("Saturation reset to original!")

            st.markdown("""---""")

            # ---------- 2ND ROW ----------
            with st.container():
                lcol, mcol, rcol = st.columns(3)
                # ---------- CONTRAST ----------
                if "contrast_slider" not in st.session_state:
                    st.session_state["contrast_slider"] = 100
                contrast_factor = lcol.slider(
                    "Drag slider to change contrast",
                    min_value=0,
                    max_value=200,
                    value=st.session_state["contrast_slider"],
                    key="contrast_slider",
                )
                contrast_img = np.asarray(
                    ImageEnhance.Contrast(Image.fromarray(saturation_img)).enhance(
                        contrast_factor / 100
                    )
                )
                lcol.image(
                    contrast_img,
                    use_column_width="auto",
                    caption=f"Contrast: {contrast_factor}%",
                )
                if lcol.button(
                    "↩️ Reset Contrast",
                    on_click=_reset,
                    use_container_width=True,
                    kwargs={"key": "contrast_slider"},
                ):
                    lcol.success("Contrast reset to original!")

                # ---------- SHARPNESS ----------
                if "sharpness_slider" not in st.session_state:
                    st.session_state["sharpness_slider"] = 100
                sharpness_factor = mcol.slider(
                    "Drag slider to change sharpness",
                    min_value=0,
                    max_value=200,
                    value=st.session_state["sharpness_slider"],
                    key="sharpness_slider",
                )
                sharpness_img = np.asarray(
                    ImageEnhance.Sharpness(Image.fromarray(contrast_img)).enhance(
                        sharpness_factor / 100
                    )
                )
                mcol.image(
                    sharpness_img,
                    use_column_width="auto",
                    caption=f"Sharpness: {sharpness_factor}%",
                )
                if mcol.button(
                    "↩️ Reset Sharpness",
                    on_click=_reset,
                    use_container_width=True,
                    kwargs={"key": "sharpness_slider"},
                ):
                    mcol.success("Sharpness reset to original!")

    st.markdown("""---""")

    # ---------- FINAL OPERATIONS ----------
    st.subheader("View Results")
    lcol, rcol = st.columns(2)
    lcol.image(
        img_arr,
        use_column_width="auto",
        caption=f"Original Image ({pil_img.size[0]} x {pil_img.size[1]})",
    )

    try:
        final_image = sharpness_img
    except NameError:
        final_image = rotated_img

    rcol.image(
        final_image,
        use_column_width="auto",
        caption=f"Final Image ({final_image.shape[1]} x {final_image.shape[0]})"
        if flag
        else f"Final Image ({final_image.size[1]} x {final_image.size[0]})",
    )

    if flag:
        Image.fromarray(final_image).save("final_image.png")
    else:
        final_image.save("final_image.png")

    col1, col2, col3 = st.columns(3)
    if col1.button(
        "↩️ Reset All", on_click=_reset, use_container_width=True, kwargs={"key": "all"}
    ):
        st.success(body="Image reset to original!", icon="↩️")
    if col2.button(
        "🔀 Surprise Me!",
        on_click=_randomize,
        use_container_width=True,
    ):
        st.success(body="Random image generated", icon="🔀")
    with open("final_image.png", "rb") as file:
        col3.download_button(
            "💾Download final image",
            data=file,
            mime="image/png",
            use_container_width=True,
        )
