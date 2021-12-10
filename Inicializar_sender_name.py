from app import db, create_app
from app.models import Company
from flask import current_app


app=create_app()
with app.app_context():


    companies = Company.query.all()
   
    for x in companies:
        if x.store_id == '1':
            continue
        print ('Comenzando '+str(x.store_id)+' '+x.store_name)

        if not x.communication_email_name : 
            mail = x.communication_email
            x.communication_email_name =  mail.split("@")[0]
            print ('sender :' + x.communication_email_name +' -'+ mail)

        db.session.commit()
        print ('Finalizado '+str(x.store_id)+' '+x.store_name)

                
        


  




