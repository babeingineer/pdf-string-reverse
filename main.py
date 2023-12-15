import fitz
def flags_decomposer(flags):
    """Make font flags human readable."""
    l = []
    if flags & 2 ** 0:
        l.append("superscript")
    if flags & 2 ** 1:
        l.append("italic")
    if flags & 2 ** 2:
        l.append("serifed")
    else:
        l.append("sans")
    if flags & 2 ** 3:
        l.append("monospaced")
    else:
        l.append("proportional")
    if flags & 2 ** 4:
        l.append("bold")
    return ", ".join(l)

def process_pdf(input_pdf, output_pdf):
    doc = fitz.open(input_pdf)
    for page_number in range(len(doc)):
        page = doc[page_number]
        text_blocks = page.get_text("dict")["blocks"]

        for block in text_blocks:
            if block["type"] == 0:  # Text block
                for line in block["lines"]:
                    for span in line["spans"]:
                        # Get text and its properties
                        original_text = span["text"]
                        rect = fitz.Rect(span["bbox"])
                        if len(original_text.strip()) > 1:
                            page.add_redact_annot(rect, fill=(1, 1, 1))
                            page.apply_redactions()
                for line in block["lines"]:
                    for span in line["spans"]:
                        # Get text and its properties
                        original_text = span["text"]
                        rect = fitz.Rect(span["bbox"])
                        font_size = span["size"]
                        flags = flags_decomposer(span["flags"])

                        # Ensure font color is in the correct format
                        font_color = span["color"]

                        r = 1 / 256 * (font_color // (256 * 256))
                        g = 1 / 256 * (font_color % (256 * 256) // 256)
                        b = 1 / 256 * (font_color % 256)
                        font_color = [r, g, b]

                        font_name = span["font"]

                        # Cover the original text with a white rectangle
                        reversed_text = original_text[::-1]
                        if len(original_text.strip()) > 1:
                            try:
                                page.insert_text(rect.bl, reversed_text, fontsize=font_size, fontname=font_name, color=font_color)
                                print(f"font ---{flags}--- '{font_name}': |{original_text}|")
                            except:
                                print(f"Error with font ---{flags}--- '{font_name}': |{original_text}|")
                                fontname = font_name.split("-")[0]
                                fontfile = "./fonts/" + fontname
                                if "-" in font_name and "Bold" in font_name.split("-")[1]:
                                    fontfile += "_Bold"
                                elif "-" in font_name and "Italic" in font_name.split("-")[1]:
                                    fontfile += "_Italic"
                                else:
                                    fontfile += "_Regular"
                                fontfile += ".ttf"
                                page.insert_text(rect.bl, reversed_text, fontsize=font_size,fontname=fontname, fontfile = fontfile, color=font_color)
    doc.save(output_pdf)
    doc.close()

# Example usage
process_pdf('test/B.pdf', 'test/output_.pdf')