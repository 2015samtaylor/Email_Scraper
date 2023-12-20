def get_intro_template(school, unique_identifier, sport):
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body{{
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
            }}

            .container {{
                background-color: #ffffff;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}

            h1 {{
                color: #007BFF;
            }}

            p {{
                font-size: 16px;
                line-height: 1.6;
            }}

            a, .underline:hover {{
                color: #007BFF;
                text-decoration: none;
            }}

            a:hover, .underline:hover {{
                text-decoration: underline;
            }}

            .image-container {{
                display: flex;
                justify-content: space-between;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>We are the supplier for all of your Baseball Apparel Needs!</h1>
            <p>Ranging from <span class="underline"> Customized Majestic Jerseys, to hats, pants, and other apparel</span>. Elevate your team's spirit with our high-quality, personalized jerseys designed to make a statement on the field.</p>
      
            <p>Ready to get started?</p>
            <p>Visit our website or give us a call to request a free sample and explore our catalog: <a href="https://customplanet.com/MLB-Jerseys-Shirts.aspx" class="underline">customplanet.com</a>.</p>
            <input type="hidden" id="hidden-uuid" value="{unique_identifier}">
            <div class="image-container">
              <a href="https://lh3.googleusercontent.com/drive-viewer/AEYmBYQmuQ4J-EYUpisQVdPrz3MmkOmf2SOnDkcm3INFs33UD-pTMvOO78vLoVOsJg91gPgdivzWj76jMHiZvdQaN7AQzE3MCA=s1600?source=screenshot.guru"> 
                <img src="https://lh3.googleusercontent.com/drive-viewer/AEYmBYQmuQ4J-EYUpisQVdPrz3MmkOmf2SOnDkcm3INFs33UD-pTMvOO78vLoVOsJg91gPgdivzWj76jMHiZvdQaN7AQzE3MCA=s1600" alt="Customplanet Culture 1" width="600px">
              </a>  
            </div>
            <p class="footer">Best Regards,<br>Your Team at Customplanet</p>
            <p class="sport-reference">Baseball season is nearly here!</p>
            <p>For inquiries, contact us at: <a href="(801) 810-8337" class="underline"> (801) 810-8337</a></p>
        </div>
    </body>
    </html>
    '''
