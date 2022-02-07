PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE alembic_version (
	version_num VARCHAR(32) NOT NULL, 
	CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);
INSERT INTO alembic_version VALUES('715f875f2d82');
CREATE TABLE company (
	store_id VARCHAR(64) NOT NULL, 
	platform VARCHAR(64), 
	platform_token_type VARCHAR(30), 
	platform_access_token VARCHAR(64), 
	store_name VARCHAR(120), 
	store_main_language VARCHAR(20), 
	store_main_currency VARCHAR(20), 
	store_country VARCHAR(20), 
	store_url VARCHAR(120), 
	store_plan VARCHAR(64), 
	store_phone VARCHAR(20), 
	store_address VARCHAR(120), 
	admin_email VARCHAR(120), 
	communication_email VARCHAR(120), 
	communication_email_name VARCHAR(120), 
	param_logo VARCHAR(200), 
	param_fondo VARCHAR(120), 
	param_config VARCHAR(120), 
	contact_name VARCHAR(64), 
	contact_phone VARCHAR(15), 
	contact_email VARCHAR(120), 
	correo_usado VARCHAR(64), 
	correo_apikey VARCHAR(50), 
	correo_id VARCHAR(50), 
	correo_test BOOLEAN, 
	correo_cost VARCHAR(15), 
	stock_vuelve_config BOOLEAN, 
	correo_apikey_test VARCHAR(50), 
	correo_id_test VARCHAR(50), 
	shipping_address VARCHAR(64), 
	shipping_number VARCHAR(64), 
	shipping_floor VARCHAR(64), 
	shipping_zipcode VARCHAR(64), 
	shipping_city VARCHAR(64), 
	shipping_province VARCHAR(64), 
	shipping_country VARCHAR(64), 
	shipping_info VARCHAR(120), 
	aprobado_note VARCHAR(250), 
	rechazado_note VARCHAR(250), 
	envio_manual_note VARCHAR(500), 
	envio_coordinar_note VARCHAR(500), 
	envio_correo_note VARCHAR(500), 
	cupon_generado_note VARCHAR(350), 
	finalizado_note VARCHAR(500), 
	confirma_manual_note VARCHAR(500), 
	confirma_coordinar_note VARCHAR(500), 
	confirma_moova_note VARCHAR(500), 
	start_date DATETIME, 
	demo_store BOOLEAN, 
	rubro_tienda VARCHAR(64), 
	plan_boris VARCHAR(64), 
	PRIMARY KEY (store_id), 
	CHECK (correo_test IN (0, 1)), 
	CHECK (stock_vuelve_config IN (0, 1)), 
	CHECK (demo_store IN (0, 1))
);
INSERT INTO company VALUES('1447373','tiendanube','bearer','cb9d4e17f8f0c7d3c0b0df4e30bcb2b036399e16','Demo Boris',NULL,NULL,NULL,'https://demoboris.mitiendanube.com',NULL,'','','erezzoni@yandex.com','soporte@borisreturns.com','Cambios Boris','',NULL,NULL,'','','erezzoni@yandex.com',NULL,'b23920003684e781d87e7e5b615335ad254bdebc','b22bc380-439f-11eb-8002-a5572ae156e7',1,NULL,0,'b23920003684e781d87e7e5b615335ad254bdebc','b22bc380-439f-11eb-8002-a5572ae156e7',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'','','','2022-01-14 21:36:33.954722',NULL,NULL,'');
INSERT INTO company VALUES('1631829','tiendanube','bearer','c4c8afc07063098d7afa72bef6fdaf67ba7e22a3','Demo de boca en boca',NULL,NULL,NULL,'https://demodebocaenboca.mitiendanube.com',NULL,NULL,NULL,NULL,'soporte@borisreturns.com','Cambios Boris',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'b23920003684e781d87e7e5b615335ad254bdebc','b22bc380-439f-11eb-8002-a5572ae156e7',1,NULL,NULL,'b23920003684e781d87e7e5b615335ad254bdebc','b22bc380-439f-11eb-8002-a5572ae156e7',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2022-01-14 21:36:33.959751',NULL,NULL,NULL);
INSERT INTO company VALUES('1','None',NULL,NULL,'Boris',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'soporte@borisreturns.com','Cambios Boris',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2022-01-14 21:36:33.961740',NULL,NULL,NULL);
CREATE TABLE correos (
	correo_id VARCHAR(15) NOT NULL, 
	correo_descripcion VARCHAR(150), 
	PRIMARY KEY (correo_id)
);
INSERT INTO correos VALUES('FAST','Fastmail');
INSERT INTO correos VALUES('NONE','None');
INSERT INTO correos VALUES('OCA','OCA');
INSERT INTO correos VALUES('MOOVA','Moova');
CREATE TABLE customer (
	id INTEGER NOT NULL, 
	platform VARCHAR(64), 
	name VARCHAR(64), 
	email VARCHAR(120), 
	identification VARCHAR(20), 
	phone VARCHAR(15), 
	PRIMARY KEY (id)
);
INSERT INTO customer VALUES(52507638,'tiendanube','Esteban Rezzonico','erezzoni@outlook.com','21444555','');
CREATE TABLE IF NOT EXISTS "CONF_boris" (
	store VARCHAR(64) NOT NULL, 
	ventana_cambios INTEGER, 
	ventana_devolucion INTEGER, 
	cambio_otra_cosa BOOLEAN, 
	cambio_cupon BOOLEAN, 
	cambio_opcion VARCHAR(150), 
	cambio_opcion_cupon VARCHAR(150), 
	cambio_opcion_otra_cosa VARCHAR(150), 
	portal_empresa VARCHAR(150), 
	portal_titulo VARCHAR(250), 
	portal_texto VARCHAR(250), 
	PRIMARY KEY (store), 
	FOREIGN KEY(store) REFERENCES company (store_id), 
	CHECK (cambio_otra_cosa IN (0, 1)), 
	CHECK (cambio_cupon IN (0, 1))
);
INSERT INTO CONF_boris VALUES('1447373',90,90,1,1,'Seleccion├í si queres cambiarlo por una variante del mismo artículo, un cup├│n u otro producto','Seleccion├í esta opci├│n para obtener un cup├│n de cr├⌐dito en nuestra tienda','Eleg├¡ en nuestra tienda el art├¡culo que quer├⌐s, ingres├í el nombre y presiona buscar','Demo Boris','Cambios y Devoluciones','Ante cualquier problema contactanos a ayuda@borisreturns.com');
CREATE TABLE IF NOT EXISTS "CONF_correo" (
	id VARCHAR(10) NOT NULL, 
	store VARCHAR(64), 
	correo_id VARCHAR(15), 
	cliente_apikey VARCHAR(100), 
	cliente_id VARCHAR(50), habilitado BOOLEAN, 
	PRIMARY KEY (id), 
	FOREIGN KEY(correo_id) REFERENCES correos (correo_id), 
	FOREIGN KEY(store) REFERENCES company (store_id)
);
INSERT INTO CONF_correo VALUES('1','1447373','FAST','ojMsr2VNOc3iYztZgANY5uzEv9zCwEpvTT9rRoaC3CPkKC7drALbGf8kzjkK','',1);
INSERT INTO CONF_correo VALUES('2','1447373','MOOVA','b23920003684e781d87e7e5b615335ad254bdebc','b22bc380-439f-11eb-8002-a5572ae156e7',1);
INSERT INTO CONF_correo VALUES('OCA1447373','1447373','OCA','12','12',1);
CREATE TABLE IF NOT EXISTS "CONF_metodos_envios" (
	store VARCHAR(64) NOT NULL, 
	metodo_envio_id VARCHAR(20) NOT NULL, 
	habilitado BOOLEAN, 
	titulo_boton VARCHAR(150), 
	descripcion_boton VARCHAR(350), 
	correo_id VARCHAR(10), 
	correo_servicio VARCHAR(50), 
	correo_sucursal VARCHAR(50), 
	costo_envio VARCHAR(15), 
	icon VARCHAR(50), 
	intrucciones_entrega TEXT, correo_descripcion VARCHAR(150), 
	PRIMARY KEY (store, metodo_envio_id), 
	FOREIGN KEY(metodo_envio_id) REFERENCES envios (metodo_envio_id), 
	FOREIGN KEY(store) REFERENCES company (store_id), 
	CHECK (habilitado IN (0, 1))
);
INSERT INTO CONF_metodos_envios VALUES('1447373','Manual',1,'Manual','boton manual','',NULL,NULL,'Merchant','bi bi-handbag',NULL,NULL);
INSERT INTO CONF_metodos_envios VALUES('1447373','Coordinar',1,'Coordinar','Boton Coordinar','',NULL,NULL,'Merchant','bi bi-headphones',NULL,NULL);
INSERT INTO CONF_metodos_envios VALUES('1447373','Retiro',1,'Retiramos en tu domiclio','Un mensajero de Fastmail retirará los prooductos de tu domiclio','FAST','LI','MA002','Merchant','bi bi-house-fill',NULL,NULL);
CREATE TABLE IF NOT EXISTS "CONF_motivos" (
	store VARCHAR(64) NOT NULL, 
	id_motivo INTEGER NOT NULL, 
	motivo VARCHAR(35), 
	tipo_motivo VARCHAR(35), 
	PRIMARY KEY (store, id_motivo), 
	FOREIGN KEY(store) REFERENCES company (store_id)
);
INSERT INTO CONF_motivos VALUES('1447373',1,'Me queda chico','Talle');
INSERT INTO CONF_motivos VALUES('1447373',2,'Me queda grande','Talle');
INSERT INTO CONF_motivos VALUES('1447373',3,'No es lo que esperaba','Expectativa');
INSERT INTO CONF_motivos VALUES('1447373',4,'No me queda bien','Calce');
INSERT INTO CONF_motivos VALUES('1447373',5,'No me gusta el color','Calce');
CREATE TABLE categories_filter (
	store VARCHAR(64) NOT NULL, 
	category_id INTEGER NOT NULL, 
	category_desc VARCHAR(100), 
	PRIMARY KEY (store, category_id), 
	FOREIGN KEY(store) REFERENCES company (store_id)
);
CREATE TABLE order_header (
	id INTEGER NOT NULL, 
	order_number INTEGER, 
	order_id_anterior INTEGER, 
	date_creation DATETIME, 
	date_closed DATETIME, 
	date_lastupdate DATETIME, 
	gastos_cupon FLOAT, 
	salientes VARCHAR(10), 
	gastos_gateway FLOAT, 
	gastos_shipping_owner FLOAT, 
	gastos_shipping_customer FLOAT, 
	gastos_promocion FLOAT, 
	payment_method VARCHAR(35), 
	payment_card VARCHAR(35), 
	courier_method VARCHAR(64), 
	metodo_envio_correo VARCHAR(64), 
	metodo_envio_guia VARCHAR(64), 
	courier_precio VARCHAR(20), 
	courier_coordinar_empresa VARCHAR(120), 
	courier_coordinar_guia VARCHAR(64), 
	courier_coordinar_roundtrip BOOLEAN, 
	nuevo_envio VARCHAR(100), 
	nuevo_envio_costo FLOAT, 
	nuevo_envio_total FLOAT, 
	status VARCHAR(25), 
	sub_status VARCHAR(25), 
	status_resumen VARCHAR(25), 
	reject_reason VARCHAR(350), 
	customer_address VARCHAR(64), 
	customer_number VARCHAR(35), 
	customer_floor VARCHAR(64), 
	customer_zipcode VARCHAR(8), 
	customer_locality VARCHAR(250), 
	customer_city VARCHAR(64), 
	customer_province VARCHAR(64), 
	customer_country VARCHAR(64), 
	note TEXT, 
	customer_id INTEGER, 
	store VARCHAR(64), 
	PRIMARY KEY (id), 
	FOREIGN KEY(customer_id) REFERENCES customer (id), 
	FOREIGN KEY(store) REFERENCES company (store_id), 
	CHECK (courier_coordinar_roundtrip IN (0, 1))
);
INSERT INTO order_header VALUES(1,243,481340223,'2022-01-12 17:39:03.752276',NULL,'2022-01-12 17:39:03.752276',0.0,'No',370.00000000000001776,0.0,0.0,0.0,'offline',NULL,'Coordinar','','','0.0',NULL,NULL,NULL,NULL,0.0,0.0,'Shipping','Solicitado','Solicitado',NULL,'Cuba','1965','','1428','','Capital Federal','Capital Federal','AR',NULL,52507638,'1447373');
INSERT INTO order_header VALUES(2,258,501299498,'2022-01-18 17:15:27.007880',NULL,'2022-01-18 17:15:27.007880',0.0,'Si',604.99999999999998223,0.0,0.0,0.0,'offline',NULL,'Retiro','Fastmail','202306718','475',NULL,NULL,1,'manual',0.0,0.0,'Shipping','Listo para retiro','En Transito',NULL,'Cuba','1965','6A','1428','Belgrano','Capital Federal','Capital Federal','AR',NULL,52507638,'1447373');
INSERT INTO order_header VALUES(3,262,516794626,'2022-01-12 17:36:48.833200',NULL,'2022-01-12 17:36:48.833200',0.0,'No',504.99999999999998223,0.0,0.0,0.0,'offline',NULL,'Retiro','Fastmail','','0.0',NULL,NULL,NULL,NULL,0.0,0.0,'Shipping','Solicitado','Solicitado',NULL,'Cuab','1965','','1428','Belgrano','Capital Federal','Capital Federal','AR',NULL,52507638,'1447373');
INSERT INTO order_header VALUES(4,264,523678671,'2022-01-12 18:10:53.874269',NULL,'2022-01-12 18:10:53.874269',0.0,'No',429.99999999999998223,0.0,0.0,0.0,'offline',NULL,'Retiro','Fastmail','','0.0',NULL,NULL,NULL,NULL,0.0,0.0,'Shipping','Solicitado','Solicitado',NULL,'Cuba','1965','','1428','','Capital Federal','Capital Federal','AR',NULL,52507638,'1447373');
INSERT INTO order_header VALUES(5,265,523679651,'2022-01-12 18:34:19.039063',NULL,'2022-01-12 18:34:19.039063',0.0,'Si',550.0,0.0,0.0,0.0,'offline',NULL,'Retiro','Fastmail','','0.0',NULL,NULL,NULL,NULL,0.0,0.0,'Shipping','Solicitado','Solicitado',NULL,'Cuab','1965','','1428','Belgrano','Capital Federal','Capital Federal','AR',NULL,52507638,'1447373');
INSERT INTO order_header VALUES(6,266,524553859,'2022-01-13 15:52:49.200290',NULL,'2022-01-13 15:52:49.200290',0.0,'Si',440.00000000000003552,0.0,0.0,0.0,'offline',NULL,'Retiro','Fastmail','','0.0',NULL,NULL,NULL,NULL,0.0,0.0,'Shipping','Solicitado','Solicitado',NULL,'Cuab','1965','','1428','Belgrano','Capital Federal','Capital Federal','AR',NULL,52507638,'1447373');
CREATE TABLE user (
	id INTEGER NOT NULL, 
	username VARCHAR(64), 
	identification VARCHAR(64), 
	email VARCHAR(120), 
	password_hash VARCHAR(128), 
	last_seen DATETIME, 
	store VARCHAR(64), 
	PRIMARY KEY (id), 
	FOREIGN KEY(store) REFERENCES company (store_id)
);
INSERT INTO user VALUES(1,'Webhook',NULL,'webhook@borisreturns.com',NULL,'2022-01-14 21:36:33.962737','1');
INSERT INTO user VALUES(2,'Esteban',NULL,'erezzoni@yahoo.com','pbkdf2:sha256:150000$Auqt4i2y$dcd33f2651964d8e03effd992cf766c6ac2f6d3f1cc12a22a8f38d09b3095048','2022-01-19 16:23:37.709914','1447373');
INSERT INTO user VALUES(3,'Leila','','leila@hotmail.com','pbkdf2:sha256:150000$m5twUxzJ$61b0d33a48d503edc6de59cc921455566f90468c4d95b606914cdc4dad55ca76','2022-01-04 14:49:10.179440','1631829');
INSERT INTO user VALUES(4,'Sebastian',NULL,'s@yahoo.com','pbkdf2:sha256:150000$hMK1i2ld$26b76c54feb8e9bba777c30a9334eb993483e4528c74108053105555d30c4407','2022-01-13 22:19:23.633308','1447373');
CREATE TABLE order_detail (
	order_line_number VARCHAR(30) NOT NULL, 
	line_number INTEGER, 
	prod_id INTEGER, 
	name VARCHAR(120), 
	variant INTEGER, 
	accion VARCHAR(10), 
	accion_cambiar_por INTEGER, 
	accion_cambiar_por_prod_id INTEGER, 
	accion_cambiar_por_desc VARCHAR(120), 
	accion_cantidad INTEGER, 
	motivo VARCHAR(50), 
	monto_a_devolver FLOAT, 
	monto_devuelto FLOAT, 
	nuevo_envio VARCHAR(100), 
	restock VARCHAR(30), 
	precio FLOAT, 
	alto FLOAT, 
	largo FLOAT, 
	profundidad FLOAT, 
	peso FLOAT, 
	promo_descuento FLOAT, 
	promo_nombre VARCHAR(120), 
	promo_precio_final FLOAT, 
	gestionado VARCHAR(10), 
	fecha_gestionado DATETIME, 
	"order" INTEGER, 
	PRIMARY KEY (order_line_number), 
	FOREIGN KEY("order") REFERENCES order_header (id)
);
INSERT INTO order_detail VALUES('4813402231',1,70390472,'Jean SKINNY ALFREDO 2 (Negro, 00)',258846866,'cambiar',1,1,'Cupón',1,'Es grande',0.0,0.0,NULL,NULL,1500.0,0.0,0.0,0.0,0.0,0.0,'',0.0,'Iniciado',NULL,1);
INSERT INTO order_detail VALUES('4813402232',2,70391624,'VESTIDO ACANTILADO (Blanco, M)',258849992,'devolver',NULL,NULL,NULL,1,'No me queda bien',2200.0000000000001776,0.0,NULL,NULL,2200.0000000000001776,0.0,0.0,0.0,0.0,0.0,'',0.0,'Iniciado',NULL,1);
INSERT INTO order_detail VALUES('5012994981',1,70391381,'REMERA GUARDIA (02, Gris)',258848617,'cambiar',258848615,70391381,'Remera Fiesta (01 - Gris)',1,'Es grande',0.0,0.0,NULL,NULL,50.0,0.0,0.0,0.0,0.0,0.0,'',0.0,'Cambiado','2022-01-18 17:17:41.855497',2);
INSERT INTO order_detail VALUES('5012994982',2,73924303,'Sweater Uno (M)',278100358,'cambiar',258846868,70390472,'Jean skinny Demouno(Negro,02)',1,'No me queda bien',0.0,0.0,NULL,NULL,3500.0,0.0,0.0,0.0,0.0,0.0,'',0.0,'Cambiado','2022-01-18 17:17:41.875607',2);
INSERT INTO order_detail VALUES('5167946261',1,70390472,'Jean skinny Demouno (Negro, 02)',258846868,'devolver',NULL,NULL,NULL,1,'No me queda bien',1500.0,0.0,NULL,NULL,1500.0,0.0,0.0,0.0,0.0,0.0,'',0.0,'Iniciado',NULL,3);
INSERT INTO order_detail VALUES('5236786711',1,73925636,'Sweater Parade (Beige, XS)',278103354,'devolver',NULL,NULL,NULL,1,'No me queda bien',2000.0,0.0,NULL,NULL,2000.0,0.0,0.0,0.0,0.0,0.0,'',0.0,'Iniciado',NULL,4);
INSERT INTO order_detail VALUES('5236786712',2,80964673,'GIft Card',314193983,'cambiar',1,1,'Cupón',1,'No me queda bien',0.0,0.0,NULL,NULL,100.0,0.0,0.0,0.0,0.0,0.0,'',0.0,'Iniciado',NULL,4);
INSERT INTO order_detail VALUES('5236796511',1,70975527,'MONO DES LILAS (S)',261651693,'cambiar',261651695,70975527,'MONO DES LILAS (L)',1,'Mala calidad',0.0,0.0,NULL,NULL,2000.0,0.0,0.0,0.0,0.0,0.0,'',0.0,'Iniciado',NULL,5);
INSERT INTO order_detail VALUES('5245538591',1,70391624,'VESTIDO ACANTILADO (Blanco, M)',258849992,'cambiar',261652248,70975791,'Jean Demo(M)',1,'Esta fallado',0.0,0.0,NULL,NULL,2200.0000000000001776,0.0,0.0,0.0,0.0,0.0,'',0.0,'Iniciado',NULL,6);
INSERT INTO order_detail VALUES('5245538592',2,70391624,'VESTIDO ACANTILADO (Blanco, S)',258849991,'cambiar',261652248,70975791,'Jean Demo(M)',1,'No me queda bien',0.0,0.0,NULL,NULL,2200.0000000000001776,0.0,0.0,0.0,0.0,0.0,'',0.0,'Iniciado',NULL,6);
CREATE TABLE transaction_log (
	id INTEGER NOT NULL, 
	sub_status VARCHAR(15), 
	status_client VARCHAR(25), 
	prod VARCHAR(64), 
	fecha DATETIME, 
	username VARCHAR(64), 
	order_id INTEGER, 
	user_id INTEGER, 
	PRIMARY KEY (id), 
	FOREIGN KEY(order_id) REFERENCES order_header (id), 
	FOREIGN KEY(user_id) REFERENCES user (id)
);
INSERT INTO transaction_log VALUES(2,'Aprobado','Tu orden fue aprobada',NULL,'2022-01-07 21:48:22.223941','Esteban',NULL,2);
INSERT INTO transaction_log VALUES(3,'Aprobado','Tu orden fue aprobada',NULL,'2022-01-07 21:49:31.014832','Esteban',NULL,2);
INSERT INTO transaction_log VALUES(4,'Orden de cambio iniciada','Se gener├│ el cambio','Remera Fiesta (01 - Gris) Se env├¡a manualmente - se descuenta stock','2022-01-07 21:49:53.199003','Esteban',NULL,2);
INSERT INTO transaction_log VALUES(5,'Orden de cambio iniciada','Se gener├│ el cambio','Sweater Uno (L) Se env├¡a manualmente - se descuenta stock','2022-01-07 21:49:53.224831','Esteban',NULL,2);
INSERT INTO transaction_log VALUES(6,'Prenda devuleta a Stock','No','REMERA GUARDIA (02, Gris) Vuelve al stock','2022-01-10 17:59:24.146317','Esteban',NULL,2);
INSERT INTO transaction_log VALUES(7,'Prenda devuleta a Stock','No','Sweater Uno (M) Vuelve al stock','2022-01-10 17:59:24.188869','Esteban',NULL,2);
INSERT INTO transaction_log VALUES(8,'Cerrado','Tu orden fue finalizada','Cerrado ','2022-01-10 17:59:24.235871','Esteban',NULL,2);
INSERT INTO transaction_log VALUES(9,'Orden de cambio iniciada','Se gener├│ el cambio','Remera Fiesta (01 - Gris) Se env├¡a manualmente','2022-01-11 10:53:42.176172','Esteban',NULL,2);
INSERT INTO transaction_log VALUES(10,'Orden de cambio iniciada','Se gener├│ el cambio','Sweater Uno (L) Se env├¡a manualmente','2022-01-11 10:53:42.199803','Esteban',NULL,2);
INSERT INTO transaction_log VALUES(11,'Recibido','Llego a nuestro dep├│sito',NULL,'2022-01-13 12:04:59.361191','Esteban',NULL,2);
INSERT INTO transaction_log VALUES(12,'Aprobado','Tu orden fue aprobada',NULL,'2022-01-13 12:05:03.794196','Esteban',NULL,2);
INSERT INTO transaction_log VALUES(13,'Prenda devuleta a Stock','No','MONO DES LILAS (S) Vuelve al stock','2022-01-13 12:05:11.255240','Esteban',NULL,2);
INSERT INTO transaction_log VALUES(14,'Recibido','Llego a nuestro dep├│sito',NULL,'2022-01-13 12:07:08.277457','Esteban',NULL,2);
INSERT INTO transaction_log VALUES(15,'Aprobado','Tu orden fue aprobada',NULL,'2022-01-13 12:07:22.411998','Esteban',NULL,2);
INSERT INTO transaction_log VALUES(16,'Recibido','Llego a nuestro dep├│sito',NULL,'2022-01-13 17:25:16.112200','Esteban',NULL,2);
INSERT INTO transaction_log VALUES(17,'Aprobado','Tu orden fue aprobada',NULL,'2022-01-13 17:25:18.795273','Esteban',NULL,2);
INSERT INTO transaction_log VALUES(18,'Prenda devuleta a Stock','No','VESTIDO ACANTILADO (Blanco, M) Vuelve al stock','2022-01-13 17:26:23.166256','Esteban',NULL,2);
INSERT INTO transaction_log VALUES(19,'Prenda devuleta a Stock','No','VESTIDO ACANTILADO (Blanco, M) Vuelve al stock','2022-01-13 17:26:23.204526','Esteban',NULL,2);
INSERT INTO transaction_log VALUES(20,'Prenda devuleta a Stock','No','VESTIDO ACANTILADO (Blanco, M) Vuelve al stock','2022-01-13 17:26:40.151291','Esteban',NULL,2);
INSERT INTO transaction_log VALUES(21,'Prenda devuleta a Stock','No','VESTIDO ACANTILADO (Blanco, M) Vuelve al stock','2022-01-13 17:26:40.195172','Esteban',NULL,2);
INSERT INTO transaction_log VALUES(22,'Prenda devuleta a Stock','No','VESTIDO ACANTILADO (Blanco, M) Vuelve al stock','2022-01-13 17:28:14.103989','Esteban',NULL,2);
INSERT INTO transaction_log VALUES(23,'Prenda devuleta a Stock','No','VESTIDO ACANTILADO (Blanco, M) Vuelve al stock','2022-01-13 17:28:15.905222','Esteban',NULL,2);
INSERT INTO transaction_log VALUES(24,'Prenda devuleta a Stock','No','VESTIDO ACANTILADO (Blanco, M) Vuelve al stock','2022-01-13 17:28:32.020283','Esteban',NULL,2);
INSERT INTO transaction_log VALUES(25,'Prenda devuleta a Stock','No','VESTIDO ACANTILADO (Blanco, M) Vuelve al stock','2022-01-13 17:28:33.815279','Esteban',NULL,2);
INSERT INTO transaction_log VALUES(26,'Recibido','Llego a nuestro dep├│sito',NULL,'2022-01-13 17:34:25.785599','Esteban',NULL,2);
INSERT INTO transaction_log VALUES(27,'Aprobado','Tu orden fue aprobada',NULL,'2022-01-13 17:34:27.295328','Esteban',NULL,2);
INSERT INTO transaction_log VALUES(28,'Prenda devuleta a Stock','No','VESTIDO ACANTILADO (Blanco, M) Vuelve al stock','2022-01-13 17:34:42.408586','Esteban',NULL,2);
INSERT INTO transaction_log VALUES(29,'Prenda devuleta a Stock','No','VESTIDO ACANTILADO (Blanco, S) Vuelve al stock','2022-01-13 17:34:44.318728','Esteban',NULL,2);
INSERT INTO transaction_log VALUES(30,'Orden de cambio iniciada','Se gener├│ el cambio','Jean Demo(M) Se env├¡a manualmente - se descuenta stock','2022-01-13 17:53:29.944299','Esteban',NULL,2);
INSERT INTO transaction_log VALUES(31,'Orden de cambio iniciada','Se gener├│ el cambio','Jean Demo(M) Se env├¡a manualmente - se descuenta stock','2022-01-13 17:53:29.974984','Esteban',NULL,2);
INSERT INTO transaction_log VALUES(32,'Cerrado','Tu orden fue finalizada','Cerrado ','2022-01-13 17:53:29.996493','Esteban',NULL,2);
INSERT INTO transaction_log VALUES(33,'Recibido','Llego a nuestro dep├│sito',NULL,'2022-01-13 19:31:00.955036','Sebastian',NULL,4);
INSERT INTO transaction_log VALUES(34,'Aprobado','Tu orden fue aprobada',NULL,'2022-01-13 19:31:02.703297','Sebastian',NULL,4);
INSERT INTO transaction_log VALUES(35,'Orden de cambio iniciada','Se gener├│ el cambio','MONO DES LILAS (L) Se env├¡a manualmente - se descuenta stock','2022-01-13 19:31:14.180351','Sebastian',NULL,4);
INSERT INTO transaction_log VALUES(36,'Orden de cambio iniciada','Se gener├│ el cambio','MONO DES LILAS (L) Se env├¡a manualmente - se descuenta stock','2022-01-13 19:34:19.980050','Sebastian',NULL,4);
INSERT INTO transaction_log VALUES(37,'Orden de cambio iniciada','Se gener├│ el cambio','MONO DES LILAS (L) Se env├¡a manualmente - se descuenta stock','2022-01-13 19:35:30.623621','Sebastian',NULL,4);
INSERT INTO transaction_log VALUES(38,'Orden de cambio iniciada','Se gener├│ el cambio','MONO DES LILAS (L) Se env├¡a manualmente - se descuenta stock','2022-01-13 19:37:50.596172','Sebastian',NULL,4);
INSERT INTO transaction_log VALUES(39,'Orden de cambio iniciada','Se gener├│ el cambio','MONO DES LILAS (L) Se env├¡a manualmente - se descuenta stock','2022-01-13 19:40:04.575083','Sebastian',NULL,4);
INSERT INTO transaction_log VALUES(40,'Orden de cambio iniciada','Se gener├│ el cambio','MONO DES LILAS (L) Se env├¡a manualmente - se descuenta stock','2022-01-13 19:51:15.945883','Sebastian',NULL,4);
INSERT INTO transaction_log VALUES(41,'Orden de cambio iniciada','Se gener├│ el cambio','Jean Demo(M) Se env├¡a manualmente - se descuenta stock','2022-01-13 19:56:20.654890','Sebastian',NULL,4);
INSERT INTO transaction_log VALUES(42,'Orden de cambio iniciada','Se gener├│ el cambio','Jean Demo(M) Se env├¡a manualmente - se descuenta stock','2022-01-13 19:56:20.674837','Sebastian',NULL,4);
INSERT INTO transaction_log VALUES(43,'Recibido','Llego a nuestro dep├│sito',NULL,'2022-01-13 21:39:08.149980','Sebastian',NULL,4);
INSERT INTO transaction_log VALUES(44,'Aprobado','Tu orden fue aprobada',NULL,'2022-01-13 21:39:09.650705','Sebastian',NULL,4);
INSERT INTO transaction_log VALUES(45,'Orden de cambio iniciada','Se gener├│ el cambio','Jean SKINNY ALFREDO 2 (Negro, 00) Se genera cupon: 243P2NZO0CW1 por un total de1500','2022-01-13 21:39:12.788827','Sebastian',NULL,4);
INSERT INTO transaction_log VALUES(46,'Prenda devuleta a Stock','No','Jean SKINNY ALFREDO 2 (Negro, 00) Vuelve al stock','2022-01-13 21:39:16.543485','Sebastian',NULL,4);
INSERT INTO transaction_log VALUES(47,'Prenda devuleta a Stock','No','VESTIDO ACANTILADO (Blanco, M) Vuelve al stock','2022-01-13 21:39:18.698564','Sebastian',NULL,4);
INSERT INTO transaction_log VALUES(48,'Cerrado','Tu orden fue finalizada','Cerrado ','2022-01-13 21:39:18.733470','Sebastian',NULL,4);
INSERT INTO transaction_log VALUES(49,'Recibido','Llego a nuestro dep├│sito',NULL,'2022-01-13 21:39:33.947334','Sebastian',NULL,4);
INSERT INTO transaction_log VALUES(50,'Aprobado','Tu orden fue aprobada',NULL,'2022-01-13 21:39:37.955230','Sebastian',NULL,4);
INSERT INTO transaction_log VALUES(51,'Orden de cambio iniciada','Se gener├│ el cambio','Remera Fiesta (01 - Azul) Se env├¡a manualmente','2022-01-13 21:39:51.106139','Sebastian',NULL,4);
INSERT INTO transaction_log VALUES(52,'Orden de cambio iniciada','Se gener├│ el cambio','Jean skinny Demouno(Negro,02) Se env├¡a manualmente','2022-01-13 21:39:51.134051','Sebastian',NULL,4);
INSERT INTO transaction_log VALUES(53,'Prenda devuleta a Stock','No','REMERA GUARDIA (02, Gris) Vuelve al stock','2022-01-13 21:40:00.038640','Sebastian',NULL,4);
INSERT INTO transaction_log VALUES(54,'Prenda devuleta a Stock','No','Sweater Uno (M) No vuelve al stock','2022-01-13 21:40:00.090500','Sebastian',NULL,4);
INSERT INTO transaction_log VALUES(55,'Cerrado','Tu orden fue finalizada','Cerrado ','2022-01-13 21:40:00.121418','Sebastian',NULL,4);
INSERT INTO transaction_log VALUES(56,'Recibido','Llego a nuestro dep├│sito',NULL,'2022-01-13 22:08:33.164619','Sebastian',NULL,4);
INSERT INTO transaction_log VALUES(57,'Aprobado','Tu orden fue aprobada',NULL,'2022-01-13 22:08:34.445906','Sebastian',NULL,4);
INSERT INTO transaction_log VALUES(58,'Recibido','Llego a nuestro dep├│sito',NULL,'2022-01-13 22:08:47.724144','Sebastian',NULL,4);
INSERT INTO transaction_log VALUES(59,'Aprobado','Tu orden fue aprobada',NULL,'2022-01-13 22:08:49.349273','Sebastian',NULL,4);
INSERT INTO transaction_log VALUES(60,'Aprobado','Tu orden fue aprobada',NULL,'2022-01-13 22:13:18.860142','Sebastian',NULL,4);
INSERT INTO transaction_log VALUES(61,'Aprobado','Tu orden fue aprobada',NULL,'2022-01-13 22:13:52.185377','Sebastian',NULL,4);
INSERT INTO transaction_log VALUES(62,'Aprobado','Tu orden fue aprobada',NULL,'2022-01-13 22:14:10.325811','Sebastian',NULL,4);
INSERT INTO transaction_log VALUES(63,'Aprobado','Tu orden fue aprobada',NULL,'2022-01-13 22:14:19.195839','Sebastian',NULL,4);
INSERT INTO transaction_log VALUES(64,'Aprobado','Tu orden fue aprobada',NULL,'2022-01-13 22:15:23.851820','Sebastian',NULL,4);
INSERT INTO transaction_log VALUES(65,'Aprobado','Tu orden fue aprobada',NULL,'2022-01-13 22:16:30.368806','Sebastian',NULL,4);
INSERT INTO transaction_log VALUES(66,'Aprobado','Tu orden fue aprobada',NULL,'2022-01-13 22:18:28.574403','Sebastian',NULL,4);
INSERT INTO transaction_log VALUES(67,'Aprobado','Tu orden fue aprobada',NULL,'2022-01-13 22:19:23.265479','Sebastian',NULL,4);
INSERT INTO transaction_log VALUES(68,'Orden de cambio iniciada','Se generó el cambio','MONO DES LILAS (L) Se envía manualmente','2022-01-17 14:47:07.649234','Esteban',NULL,2);
INSERT INTO transaction_log VALUES(69,'Recibido','Llego a nuestro depósito',NULL,'2022-01-17 16:30:39.654588','Esteban',NULL,2);
INSERT INTO transaction_log VALUES(70,'Orden de cambio iniciada','Se generó el cambio','MONO DES LILAS (L) Se envía manualmente','2022-01-17 16:42:29.080983','Esteban',NULL,2);
INSERT INTO transaction_log VALUES(71,'Orden de cambio iniciada','Se generó el cambio','Jean Demo(M) Se envía manualmente','2022-01-17 16:44:43.561312','Esteban',NULL,2);
INSERT INTO transaction_log VALUES(72,'Orden de cambio iniciada','Se generó el cambio','Jean Demo(M) Se envía manualmente','2022-01-17 16:44:43.598134','Esteban',NULL,2);
INSERT INTO transaction_log VALUES(73,'Orden de cambio iniciada','Se generó el cambio','MONO DES LILAS (L) Se envía manualmente','2022-01-17 16:50:11.413156','Esteban',NULL,2);
INSERT INTO transaction_log VALUES(74,'Orden de cambio iniciada','Se generó el cambio','Jean Demo(M) Se envía manualmente','2022-01-17 17:00:45.364024','Esteban',NULL,2);
INSERT INTO transaction_log VALUES(75,'Orden de cambio iniciada','Se generó el cambio','Jean Demo(M) Se envía manualmente','2022-01-17 17:00:45.391884','Esteban',NULL,2);
INSERT INTO transaction_log VALUES(76,'Orden de cambio iniciada','Se generó el cambio','Remera Fiesta (01 - Gris) Se envía manualmente','2022-01-18 17:17:41.857492','Esteban',2,2);
INSERT INTO transaction_log VALUES(77,'Orden de cambio iniciada','Se generó el cambio','Jean skinny Demouno(Negro,02) Se envía manualmente','2022-01-18 17:17:41.877602','Esteban',2,2);
CREATE TABLE metodos_envios (
	metodo_envio_id VARCHAR(20) NOT NULL, 
	metodo_envio_descripcion VARCHAR(200), 
	carrier BOOLEAN, 
	direccion_obligatoria BOOLEAN, 
	icon VARCHAR(50), 
	PRIMARY KEY (metodo_envio_id), 
	CHECK (carrier IN (0, 1)), 
	CHECK (direccion_obligatoria IN (0, 1))
);
INSERT INTO metodos_envios VALUES('Manual','El cliente se ocupa de llevar los productos',0,0,'bi bi-handbag');
INSERT INTO metodos_envios VALUES('Coordinar','A coordianr',0,1,'bi bi-headphones');
INSERT INTO metodos_envios VALUES('Retiro','Retiro por el domiclio del Ciente',1,1,'bi bi-house-fill');
INSERT INTO metodos_envios VALUES('Etiqueta','Etiquetas Prepagas',1,1,NULL);
INSERT INTO metodos_envios VALUES('Locales','El cliente selecciona un local',0,0,NULL);
CREATE INDEX ix_company_platform ON company (platform);
CREATE INDEX ix_company_store_id ON company (store_id);
CREATE INDEX ix_customer_email ON customer (email);
CREATE INDEX ix_customer_name ON customer (name);
CREATE INDEX ix_customer_platform ON customer (platform);
CREATE INDEX ix_order_header_metodo_envio_guia ON order_header (metodo_envio_guia);
CREATE INDEX ix_order_header_order_number ON order_header (order_number);
CREATE INDEX ix_user_email ON user (email);
CREATE INDEX ix_user_id ON user (id);
CREATE INDEX ix_user_identification ON user (identification);
CREATE UNIQUE INDEX ix_user_username ON user (username);
COMMIT;
