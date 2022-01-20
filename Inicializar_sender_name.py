from app import db, create_app
from app.models import Company, CONF_boris
from flask import current_app
from app.main.interfaces import actualiza_empresa_JSON


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
       

        actualiza_empresa_JSON(x, 'portal_empresa', x.store_name, 'textos')
        actualiza_empresa_JSON(x, 'portal_titulo', 'Cambios y Devoluciones', 'textos')
        

        empresa = CONF_boris.query.filter_by(store=x.store_id).first()
        empresa.portal_empresa = x.store_name
        empresa.portal_titulo = 'Cambios y Devoluciones'
        
        if x.envio_coordinar_note :
            x.envio_coordinar_note = '1 - Embalá tu producto correctamente<br>'+ x.envio_coordinar_note
        else: 
            x.envio_coordinar_note = '1 - Embalá tu producto correctamente<br>'
        print(x.envio_coordinar_note)

        db.session.commit()


        print ('Finalizado '+str(x.store_id)+' '+x.store_name)

                
        


  




