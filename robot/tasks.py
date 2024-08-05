from robocorp.tasks import task
from robocorp import browser, log
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.

    https://robocorp.com/docs/courses/build-a-robot-python/create-order-process
    """
    browser.configure(slowmo=200)
    open_robot_order_website()
    download_orders_file()
    orders = read_orders_file()
    loop_fill_csv_data(orders)
    archive_receipts()

def log_info(message):
    log.info(message)

def close_annoying_modal():
    page = browser.page()
    page.click('text=OK')

def open_robot_order_website():
    browser.goto("https://robotsparebinindustries.com/#/robot-order")
    close_annoying_modal()

def download_orders_file():
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)

def read_orders_file():
    csv_file = Tables()
    robot_orders = csv_file.read_table_from_csv("orders.csv")
    return robot_orders

def loop_fill_csv_data(orders):
    log_info(orders)
    for order in orders:
        fill_the_form(order)
    
def click_ok():
    page = browser.page()
    page.click('text=OK')

def screenshot_robot(order_number):
    page = browser.page()
    screenshot_path = "output/screenshots/{0}.png".format(order_number)
    page.locator("#robot-preview-image").screenshot(path=screenshot_path)
    return screenshot_path

def store_receipt_as_pdf(order):
    page = browser.page()
    order_receipt_html = page.locator("#receipt").inner_html()
    pdf = PDF()
    pdf_path = "output/receipts/{0}.pdf".format(order["Order number"])
    pdf.html_to_pdf(order_receipt_html, pdf_path)
    return pdf_path


def submit_order_another(order):
    page = browser.page()
    page.click('#order')
    order_another = page.query_selector("#order-another")
    if order_another:
        pdf_path = store_receipt_as_pdf(order)
        screenshot_path = screenshot_robot(int(order["Order number"]))
        pdf = PDF()
        pdf.add_watermark_image_to_pdf(image_path=screenshot_path, source_path=pdf_path, output_path=pdf_path)
        page.click('#order-another')
        click_ok()

def fill_the_form(order):
    page = browser.page()
    page.select_option('#head', order['Head'])
    page.click('//*[@id="root"]/div/div[1]/div/div[1]/form/div[2]/div/div[{0}]/label'.format(order["Body"]))
    page.fill("input[placeholder='Enter the part number for the legs']", order["Legs"])
    page.fill("#address", order["Address"])
    while True: #Infinite loop (always true) until Break
        submit_order_another(order)
        break

def archive_receipts():
    lib = Archive()
    lib.archive_folder_with_zip("./output/receipts", "./output/receipts.zip")

        
