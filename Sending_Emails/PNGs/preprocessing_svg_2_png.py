# Pre-processing (Convert SVG to PNG)

import pandas as pd
import aspose.words as aw
pd.set_option('display.max_columns', None)
df = pd.read_csv('KC SCHOOLS - KC SCHOOLS.csv')
df = df.replace(r'^\s+$', np.nan, regex=True)
df = df.replace('?', np.nan)
df = df.replace('-', np.nan)
df = df.iloc[:836]



# Take all SVG images in 'OUR LOGO column' and convert them to PNG

def SVG_2_PNG():
    i = 0
    while i < len(df['OUR LOGO']):
    
        try: 
            fileName = df['OUR LOGO'][i]
            doc = aw.Document()
            builder = aw.DocumentBuilder(doc)
            shape = builder.insert_image(fileName)
            doc.save("PNGs/{}.png".format(str(i) + ' '+ df['High schools'][i]))
        except TypeError:
            pass
        except RuntimeError:
            pass

        i +=1

SVG_2_PNG()