from PIL import Image, ImageDraw, ImageFont
import boto3
from pprint import pprint, pformat
from io import BytesIO
import image_helpers
import requests

# --------------------------------------------------------------------
# DO NOT CHANGE THESE FUNCTIONS

def image_upload(image_path,ftype):
    #ftype tell about image is URL or file 
    s3 = session.client('s3')
    s3_res = session.resource('s3')
    if ftype == "url":
        name = str(image_path).split('/')[len(str(image_path).split('/')) - 1]
        buffered = BytesIO(requests.get(image_path).content)
        s3.upload_fileobj(buffered, BUCKET, name)
    else:
        name = str(image_path).split('/')[len(str(image_path).split('/')) - 1]
        s3_res.meta.client.upload_file(image_path, BUCKET, name)
    #image = Image.open(buffered)
    #image.save('reck.png')
    #s3.upload_fileobj(buffered, 'amazon-rekognition12', 'test_pic3.png')
    response=s3.put_object_acl(
        ACL='public-read',
        Bucket=BUCKET,
        Key=name
    )
    #p(response)
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        print("Image has been uploaded to S3")
        return name

def format_text(text, columns):
    '''
    Returns a copy of text that will not span more than the specified number of columns
    :param text: the text
    :param columns: the maximum number of columns
    :return: the formatted text
    '''
    # format the text to fit the specified columns
    import re
    text = re.sub('[()\']', '', pformat(text, width=columns))
    text = re.sub('\n ', '\n', text)
    return text


def text_rect_size(draw, text, font):
    '''
    Returns the size of the rectangle to be used to
    draw as the background for the text
    :param draw: an ImageDraw.Draw object
    :param text: the text to be displayed
    :param font: the font to be used
    :return: the size of the rectangle to be used to draw as the background for the text
    '''
    (width, height) = draw.multiline_textsize(text, font=font)
    return (width * 1.1, height * 1.3)


def add_text_to_img(img, text, pos=(0, 0), color=(0, 0, 0), bgcolor=(255, 255, 255, 128),
                    columns=60,
                    font=ImageFont.truetype('ariblk.ttf', 22)):
    '''
    Creates and returns a copy of the image with the specified text displayed on it
    :param img: the (Pillow) image
    :param text: the text to display
    :param pos: a 2 tuple containing the xpos, and ypos of the text
    :param color: the fill color of the text
    :param bgcolor: the background color of the box behind the text
    :param columns: the max number of columns for the text
    :param font: the font to use
    :return: a copy of the image with the specified text displayed on it
    '''

    # make a blank image for the text, initialized to transparent text color
    txt_img = Image.new('RGBA', img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(txt_img)

    # format the text
    text = format_text(text, columns)
    # get the size of the text drawn in the specified font
    (text_width, text_height) = ImageDraw.Draw(img).multiline_textsize(text, font=font)

    # compute positions and box size
    (xpos, ypos) = pos
    rwidth = text_width * 1.1
    rheight = text_height * 1.4
    text_xpos = xpos + (rwidth - text_width) / 2
    text_ypos = ypos + (rheight - text_height) / 2

    # draw the rectangle (slightly larger) than the text
    draw.rectangle([xpos, ypos, xpos + rwidth, ypos + rheight], fill=bgcolor)

    # draw the text on top of the rectangle
    draw.multiline_text((text_xpos, text_ypos), text, font=font, fill=color)

    del draw # clean up the ImageDraw object
    return Image.alpha_composite(img.convert('RGBA'), txt_img)


def get_pillow_img(imgbytes):
    """
    Creates and returns a Pillow image from the given image bytes
    :param imgbytes: the bytes of the image
    """
    return Image.open(BytesIO(imgbytes))


# NOTE: YOU DON'T NEED TO USE THIS (round_conf) FUNCTION,
#       IT IS ONLY USED BY THE DOCTESTS!
def round_conf(conf):
    """
    NOTE: YOU DON'T NEED TO USE THIS FUNCTION, IT
          IS ONLY USED BY THE DOCTESTS!

    Given a dictionary with keys Name and Confidence,
    returns a new dictionary with unchanged Name and the Confidence value rounded
    :param conf: a dictionary with keys Name and Confidence
    :return: a new dictionary with unchanged Name and the Confidence value rounded
    """
    return {'Name': conf['Name'], 'Confidence': round(conf['Confidence'])}


# END DO NOT CHANGE SECTION
# --------------------------------------------------------------------

def get_labels(img, confidence=50):
    # replace pass below with your implementation
    if img.find(":") == -1:
        ftype="file"
    else:
        ftype="url"
        
    KEY = image_upload(img,ftype)
    rekognition = session.client("rekognition")
    response = rekognition.detect_labels(
		Image={
			"S3Object": {
				"Bucket": BUCKET,
				"Name": KEY,
			}
		},
		MaxLabels=10,
		MinConfidence=confidence,
    )
    
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        print(response['Labels'])
        #round_conf(response['Labels'])
        return response['Labels']


def label_image(img):
    '''
    Creates and returns a copy of the image, with labels from Rekognition displayed on it
    :param img: a string that is either the URL or filename for the image
    :return: a copy of the image, with labels from Rekognition displayed on it
    '''
    # replace pass below with your implementation
    ## Getting Labels
    label=get_labels(img)
    message=""
    for i in label:
        if i == label[len(label)-1]:
            message=message+i['Name']
        else:
            message=message+i['Name']+", "
    ## Getting Image bytes
    imgbytes=image_helpers.get_image(img)
    images=get_pillow_img(imgbytes)

    return add_text_to_img(images, message)
    


if __name__ == "__main__":
    # can't use input since PyCharm's console causes problems entering URLs
    # img = input('Enter either a URL or filename for an image: ')

    region="eu-west-1"
    session = boto3.Session(region_name=region)
    BUCKET = "amazon-rekognition12"
    KEY=""
    img = 'https://blog.njsnet.co/content/images/2017/02/trumprecognition.png'
    img = 'https://www.parrots.org/images/uploads/dreamstime_C_47716185.jpg'
    labelled_image = label_image(img)
    labelled_image.show()
