def get_receipt(courseData, fees):
    text = ""
    for index, c in enumerate(courseData):
        text += "<tr><td>" + str(index+1) + ".</td><td>" + c["courseId"] + "</td><td> Rs. " + str(c["courseFees"]) +" </td></tr>"

    text += "<tr><td>Total </td><td> </td><td> Rs. " + str(fees) +" </td></tr>"

    html = """
    <H1 align="center">ViKiNgS</H1>
    <h2 align="center">Payment Successful</h2>


        <table border="0" align="center" width="50%">
    <thead><tr><th width="30%">SR No</th><th width="40%">Course Name</th><th width="40%">Course Price</th></tr></thead>
    <tbody>
    """ + text + """
    </tbody>
    </table>
    """

    from fpdf import FPDF, HTMLMixin

    class MyFPDF(FPDF, HTMLMixin):
        pass
                        
    pdf = MyFPDF()
    #First page
    pdf.add_page()
    pdf.write_html(html)
    pdf.output('static/paymentMedia/receipt.pdf', 'F')