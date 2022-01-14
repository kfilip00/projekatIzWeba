from flask import Flask, render_template, url_for,request,redirect,redirect,session,Response
from flask_mail import Mail,Message
from werkzeug.security import generate_password_hash,check_password_hash
import mysql.connector
import mariadb
import ast
import os
import io
import csv

#deklaracija flask aplikacije
app = Flask(__name__)

konekcija = mysql.connector.connect(
    passwd="", # lozinka za bazu
    user="root", # korisničko ime
    database="evidencija_studenata", # ime baze
    port=3306, # port na kojem je mysql server
    auth_plugin='mysql_native_password' # ako se koristi mysql 8.x
)

kursor = konekcija.cursor(dictionary=True)

app.secret_key = "tajni_kljuc_aplikacije"

UPLOAD_FOLDER = "static/uploads/"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USERNAME"] = "rr2inaf0001@gmail.com"
app.config["MAIL_PASSWORD"] = "mikica123"
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USE_SSL"] = True
mail = Mail(app)

#definicija ruta




#---------------KORISNICI-----------------

@app.route("/korisnici", methods=["GET"])
def korisnici():
    if (rola() != "administrator"):
        return redirect(url_for("studenti"))
    if ulogovan():


        strana = request.args.get("page", "1")
        offset = int(strana) * 10 - 10
        prethodna_strana = ""
        sledeca_strana = "/korisnici?page=2"
        if "=" in request.full_path:
            split_path = request.full_path.split("=")
            del split_path[-1]
            sledeca_strana = "=".join(split_path) + "=" + str(int(strana) + 1)
            prethodna_strana = "=".join(split_path) + "=" + str(int(strana) - 1)


        offset=int(strana)*10-10

        args = request.args.to_dict()
        order_by = "ime"
        order_type = "asc"
        if "order_by" in args:
            order_by = args["order_by"].lower()
            if ("prethodni_order_by" in args and args["prethodni_order_by"] == args["order_by"]):
                if args["order_type"] == "asc":
                    order_type = "desc"

        upit="SELECT * FROM korisnici ORDER BY "+str(order_by)+" "+str(order_type)+" LIMIT 10 OFFSET %s"
        vrednost=(offset,)

        kursor.execute(upit,vrednost)
        korisnici=kursor.fetchall()

        return render_template("korisnici.html",
            korisnici=korisnici,
            strana=strana,
            sledeca_strana=sledeca_strana,
            prethodna_strana=prethodna_strana,
            order_type=order_type,
            args=args)
    else:
        return redirect(url_for('login'))

@app.route("/korisnik_novi", methods=["GET","POST"])
def korisnik_novi():
    if (rola() != "administrator"):
        return redirect(url_for("studenti"))
    if ulogovan():
        if(request.method=="GET"):
            return render_template("korisnik_novi.html")

        if(request.method=="POST"):
            forma=request.form
            hesovana_lozinka=generate_password_hash(forma["inputPassword"])
            vrednosti=(
                forma["inputIme"],
                forma["inputPrezime"],
                forma["inputEmail"],
                forma["inputRola"],
                hesovana_lozinka
            )
            if(forma["inputRola"]=="student"):
                podaci={
                "ime":forma["inputIme"],
                "prezime":forma["inputPrezime"],
                "email":forma["inputEmail"],
                "rola":forma["inputRola"],
                "lozinka":hesovana_lozinka
                }
                return redirect(url_for("student_novi",podaci=podaci))
            upit="INSERT INTO korisnici(ime,prezime,email,rola,lozinka) values(%s,%s,%s,%s,%s)"
            kursor.execute(upit,vrednosti)
            konekcija.commit()

            send_email(forma["inputIme"], forma["inputPrezime"], forma["inputEmail"],forma["inputPassword"])

            return redirect(url_for("korisnici"))
    else:
        return redirect(url_for('login'))



@app.route("/korisnik_izmena/<id>", methods=["GET","POST"])
def korisnik_izmena(id):
    if (rola() != "administrator"):
        return redirect(url_for("studenti"))
    if ulogovan():
        if(request.method=="GET"):
            upit="SELECT * FROM korisnici where id=%s"
            vrednost=(id,)
            kursor.execute(upit,vrednost)
            korisnik=kursor.fetchone()

            return render_template("korisnik_izmena.html",korisnik=korisnik)


        if(request.method=="POST"):
            upit="UPDATE `korisnici` SET `ime`=%s,`prezime`=%s,`email`=%s,`rola`=%s WHERE id=%s"
            forma=request.form
            vrednosti=(
                forma["inputIme"],
                forma["inputPrezime"],
                forma["inputEmail"],
                forma["inputRola"],
                id
            )
            kursor.execute(upit,vrednosti)
            konekcija.commit()


            if (forma["inputRola"]=="student"):
                upit="UPDATE `studenti` SET `ime`=%s,`prezime`=%s,`email`=%s WHERE korisnik_id=%s"
                forma=request.form
                vrednosti=(
                    forma["inputIme"],
                    forma["inputPrezime"],
                    forma["inputEmail"],
                    id
                )
                kursor.execute(upit,vrednosti)
                konekcija.commit()

            return redirect(url_for("korisnici"))
    else:
        return redirect(url_for('login'))



@app.route("/korisnik_obrisi/<id>", methods=["GET"])
def korisnik_obrisi(id):
    if (rola() != "administrator"):
        return redirect(url_for("studenti"))
    if ulogovan():
        upit="DELETE FROM `korisnici` WHERE id=%s"
        vrednosti=(id,)
        kursor.execute(upit,vrednosti)
        konekcija.commit()
        return  redirect(url_for("korisnici"))
    else:
        return redirect(url_for('login'))




#---------------PREDMETI-----------------



@app.route("/predmeti", methods=["GET"])
def predmeti():
    if (rola() != "administrator"):
        return redirect(url_for("studenti"))
    if ulogovan():


        args = request.args.to_dict()
        order_by = "sifra"
        order_type = "asc"
        if "order_by" in args:
            order_by = args["order_by"].lower()
            if ("prethodni_order_by" in args and args["prethodni_order_by"] == args["order_by"]):
                if args["order_type"] == "asc":
                    order_type = "desc"


        strana = request.args.get("page", "1")
        prethodna_strana = ""
        sledeca_strana = "/predmeti?page=2"
        if "=" in request.full_path:
            split_path = request.full_path.split("=")
            del split_path[-1]
            sledeca_strana = "=".join(split_path) + "=" + str(int(strana) + 1)
            prethodna_strana = "=".join(split_path) + "=" + str(int(strana) - 1)



        offset=int(strana)*4-4
        upit="SELECT * FROM predmeti ORDER BY "+str(order_by)+" "+str(order_type)+" LIMIT 4 OFFSET %s"
        vrednost=(offset,)
        kursor.execute(upit,vrednost)
        predmeti=kursor.fetchall()
        return render_template("predmeti.html",
        predmeti=predmeti,
        strana=strana,
        sledeca_strana= sledeca_strana,
        prethodna_strana= prethodna_strana,
        order_type=order_type,
        args=args
        )
    else:
        return redirect(url_for('login'))


@app.route("/predmet_novi", methods=["GET","POST"])
def predmet_novi():
    if (rola() != "administrator"):
        return redirect(url_for("studenti"))
    if ulogovan():
        if(request.method=="GET"):
            return render_template("predmet_novi.html")

        if(request.method=="POST"):
            forma=request.form
            upit="INSERT INTO `predmeti`(`sifra`, `naziv`, `godina_studija`, `espb`, `obavezni_izborni`) VALUES (%s,%s,%s,%s,%s)"
            vrednosti=(
                forma["inputSifra"],
                forma["inputNaziv"],
                forma["inputGodinaStudija"],
                forma["inputESPB"],
                forma["inputStatusPredmeta"]
            )
            kursor.execute(upit,vrednosti)
            konekcija.commit()

            return  redirect(url_for("predmeti"))
    else:
        return redirect(url_for('login'))


@app.route("/predmet_izmena/<sifra>",methods={"GET","POST"})
def predmet_izmena(sifra):
    if (rola() != "administrator"):
        return redirect(url_for("studenti"))
    if ulogovan():
        if(request.method=="GET"):
            upit="SELECT * FROM predmeti where sifra=%s"
            vrednost=(sifra,)
            kursor.execute(upit,vrednost)
            predmet=kursor.fetchone()
            return render_template("predmet_izmena.html",predmet=predmet)

        if(request.method=="POST"):
            upit="UPDATE `predmeti` SET `sifra`=%s,`naziv`=%s,`godina_studija`=%s,`espb`=%s,`obavezni_izborni`=%s WHERE id=%s"
            forma=request.form
            vrednosti=(
                forma["inputSifra"],
                forma["inputNaziv"],
                forma["inputGodinaStudija"],
                forma["inputESPB"],
                forma["inputStatusPredmeta"],
                sifra
            )
            kursor.execute(upit,vrednosti)
            konekcija.commit()

            return redirect(url_for("predmeti"))
    else:
        return redirect(url_for('login'))


@app.route("/predmet_obrisi/<id>", methods=["GET"])
def predmet_obrisi(id):
    if (rola() != "administrator"):
        return redirect(url_for("studenti"))
    if ulogovan():
        upit="DELETE FROM `predmeti` WHERE id=%s"
        vrednost=(id,)
        kursor.execute(upit,vrednost)
        konekcija.commit()

        return redirect(url_for("predmeti"))
    else:
        return redirect(url_for('login'))



#---------------STUDENTI-----------------


@app.route("/studenti", methods=["GET"])
def studenti():
    if ulogovan():

        if (rola() == "student"):
            id=ast.literal_eval(session["ulogovani_korisnik"]).pop("id")
            upit="SELECT id FROM studenti WHERE korisnik_id=%s"
            vrednost=(id,)

            kursor.execute(upit,vrednost)
            rezultat=kursor.fetchone()
            studenti_id=rezultat.get('id')
            return redirect(url_for("student_pregled",id=studenti_id,rola=rola()))


        args = request.args.to_dict()

        s_ime="%%"
        if "ime" in args:
            s_ime = "%" + args["ime"] + "%"

        s_prezime="%%"
        if "prezime" in args:
            s_prezime = "%" + args["prezime"] + "%"

        s_broj_indeksa="%%"
        if "broj_indeksa" in args:
            s_broj_indeksa = "%" + args["broj_indeksa"] + "%"

        s_godina_studija="%%"
        if "godina_studija" in args:
        	s_godina_studija = "%" + args["godina_studija"] + "%"

        s_espb_od="0"
        if "espb_od" in args:
            if args["espb_od"]=="":
                s_espb_od="0"
            else:
        	    s_espb_od =args["espb_od"]

        s_espb_do="240"
        if "espb_do" in args:
            if args["espb_do"]=="":
                s_espb_do="240"
            else:
        	    s_espb_do =args["espb_do"]


        s_prosek_ocena_od="0"
        if "prosek_ocena_od" in args:
            if args["prosek_ocena_od"]=="":
                s_prosek_ocena_od="0"
            else:
        	    s_prosek_ocena_od =args["prosek_ocena_od"]


        s_prosek_ocena_do="10"
        if "prosek_ocena_do" in args:
            if args["prosek_ocena_do"]=="":
                s_prosek_ocena_do="10"
            else:
        	    s_prosek_ocena_do = args["prosek_ocena_do"]



        order_by = "sifra"
        order_type = "asc"
        if "order_by" in args:
            order_by = args["order_by"].lower()
            if ("prethodni_order_by" in args and args["prethodni_order_by"] == args["order_by"]):
                if args["order_type"] == "asc":
                    order_type = "desc"


        order_by = "ime"
        order_type = "asc"
        if "order_by" in args:
            order_by = args["order_by"].lower()
            if ("prethodni_order_by" in args and args["prethodni_order_by"] == args["order_by"]):
                if args["order_type"] == "asc":
                    order_type = "desc"


        strana = request.args.get("page", "1")
        prethodna_strana = ""
        sledeca_strana = "/studenti?page=2"

        if "=" in request.full_path:
            split_path = request.full_path.split("=")
            del split_path[-1]
            sledeca_strana = "=".join(split_path) + "=" + str(int(strana) + 1)
            prethodna_strana = "=".join(split_path) + "=" + str(int(strana) - 1)

        offset=int(strana)*10-10
        upit="SELECT * from studenti WHERE ime LIKE %s AND prezime LIKE %s AND broj_indeksa LIKE %s AND godina_studija LIKE %s AND espb>= %s AND espb<= %s AND prosek_ocena>= %s AND prosek_ocena<=%s ORDER BY "+str(order_by)+" "+str(order_type)+" LIMIT 10 OFFSET %s"
        vrednost=(s_ime,
        s_prezime,
        s_broj_indeksa,
        s_godina_studija,
        s_espb_od,
        s_espb_do,
        s_prosek_ocena_od,
        s_prosek_ocena_do,
        offset,
        )
        kursor.execute(upit,vrednost)
        studenti=kursor.fetchall()

        return render_template("studenti.html",
        studenti=studenti,
         rola=rola(),
         strana=strana,
         sledeca_strana=sledeca_strana,
         prethodna_strana=prethodna_strana,
         order_type=order_type,
         args=args)
    else:
        return redirect(url_for('login'))


@app.route("/student_novi/<podaci>", methods=["GET","POST"])
def student_novi(podaci):
    if (rola() != "administrator"):
        return redirect(url_for("studenti"))
    if ulogovan():
        if(request.method=="GET"):

            res = ast.literal_eval(podaci)
            return render_template("student_novi.html",student=None,podaci=res)

        if(request.method=="POST"):

            res = ast.literal_eval(podaci)
            forma=request.form

            upit="INSERT INTO korisnici(ime,prezime,email,rola,lozinka) values(%s,%s,%s,%s,%s)"
            vrednosti=(
            forma["inputIme"],
            forma["inputPrezime"],
            forma["inputEmail"],
            res["rola"],
            res["lozinka"]
            )
            kursor.execute(upit,vrednosti)
            konekcija.commit()


            upit="SELECT id FROM korisnici WHERE email=%s"
            vrednost=(forma["inputEmail"],)

            kursor.execute(upit,vrednost)
            rezultat=kursor.fetchone()
            korisnik_id=rezultat.get('id')

            upit="INSERT INTO `studenti`(`ime`, `ime_roditelja`, `prezime`, `broj_indeksa`, `godina_studija`, `jmbg`, `datum_rodjenja`,   `broj_telefona`, `email`,`espb`,`prosek_ocena`,`slika`,`korisnik_id`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

            naziv_slike = ""
            if "slika" in request.files:
                file = request.files["slika"]
                if file.filename:
                    naziv_slike = forma["inputJMBG"] + file.filename
                    file.save(os.path.join(app.config["UPLOAD_FOLDER"], naziv_slike))
            vrednosti=(
                forma["inputIme"],
                forma["inputImeRoditelja"],
                forma["inputPrezime"],
                forma["inputBrIndeksa"],
                forma["inputGodinaStudija"],
                forma["inputJMBG"],
                forma["inputDatumRodjenja"],
                forma["inputBrojTelefona"],
                forma["inputEmail"],
                forma["inputESPB"],
                forma["inputProsekOcena"],
                naziv_slike,
                korisnik_id
            )

            kursor.execute(upit,vrednosti)
            konekcija.commit()

            send_email(forma["inputIme"], forma["inputPrezime"], forma["inputEmail"],res["lozinka"])

            return redirect(url_for("studenti"))
    else:
        return redirect(url_for('login'))


@app.route("/student_izmena/<id>", methods=["GET","POST"])
def student_izmena(id):
    if (rola() == "profesor"):
        return redirect(url_for("studenti"))
    if ulogovan():
        if(request.method=="GET"):
            upit="SELECT * FROM `studenti` WHERE id=%s"
            vrednost=(id,)
            kursor.execute(upit,vrednost)
            student=kursor.fetchone()

            return render_template("student_izmena.html",student=student,rola=rola())

        if(request.method=="POST"):


            upit="UPDATE `studenti` SET `ime`=%s,`ime_roditelja`=%s,`prezime`=%s,`broj_indeksa`=%s,`godina_studija`=%s,`jmbg`=%s,`datum_rodjenja`=%s,`espb`=%s,`prosek_ocena`=%s,`broj_telefona`=%s,`email`=%s,`slika`=%s WHERE id=%s"
            forma=request.form
            naziv_slike = ""
            if "slika" in request.files:
                file = request.files["slika"]
                if file.filename:
                    naziv_slike = forma["inputJMBG"] + file.filename
                    file.save(os.path.join(app.config["UPLOAD_FOLDER"], naziv_slike))
            vrednosti=(
                forma["inputIme"],
                forma["inputImeRoditelja"],
                forma["inputPrezime"],
                forma["inputBrIndeksa"],
                forma["inputGodinaStudija"],
                forma["inputJMBG"],
                forma["inputDatumRodjenja"],
                forma["inputESPB"],
                forma["inputProsekOcena"],
                forma["inputBrojTelefona"],
                forma["inputEmail"],
                naziv_slike,
                id
            )
            kursor.execute(upit,vrednosti)
            konekcija.commit()


            upit="SELECT korisnik_id FROM studenti WHERE id=%s"
            vrednost=(id,)

            kursor.execute(upit,vrednost)
            rezultat=kursor.fetchone()
            korisnik_id=rezultat.get('korisnik_id')



            upit="UPDATE `korisnici` SET `ime`=%s,`prezime`=%s,`email`=%s where id=%s"
            vrednosti=(
            forma["inputIme"],
            forma["inputPrezime"],
            forma["inputEmail"],
            korisnik_id
            )

            kursor.execute(upit,vrednosti)
            konekcija.commit()

            return  redirect(url_for("studenti"))
    else:
        return redirect(url_for('login'))




@app.route("/student_pregled/<id>", methods=["GET","POST"])
def student_pregled(id):
    if ulogovan():
        if(request.method=="GET"):
            upit="SELECT * FROM studenti WHERE id=%s"
            vrednost=(id,)

            kursor.execute(upit,vrednost)
            student=kursor.fetchone()

            upit="SELECT * FROM predmeti"

            kursor.execute(upit)
            predmeti=kursor.fetchall()

            args = request.args.to_dict()

            order_by = "sifra"
            order_type = "asc"
            if "order_by" in args:
                order_by = args["order_by"].lower()
                if ("prethodni_order_by" in args and args["prethodni_order_by"] == args["order_by"]):
                    if args["order_type"] == "asc":
                         order_type = "desc"

            o_sifra="%%"
            if "sifra" in args:
                o_sifra = "%" + args["sifra"] + "%"

            o_godina_studija="%%"
            if "godina_studija" in args:
                o_godina_studija = "%" + args["godina_studija"] + "%"

            o_ocena_od="0"
            if "ocena_od" in args:
                if args["ocena_od"]=="":
                    o_ocena_od="0"
                else:
            	    o_ocena_od =args["ocena_od"]

            o_ocena_do="10"
            if "ocena_do" in args:
            	if args["ocena_do"]=="":
            		o_ocena_do="10"
            	else:
            		o_ocena_do =args["ocena_do"]


            o_espb_od="0"
            if "espb_od" in args:
            	if args["espb_od"]=="":
            		o_espb_od="0"
            	else:
            		o_espb_od =args["espb_od"]

            o_espb_do="240"
            if "espb_do" in args:
            	if args["espb_do"]=="":
            		o_espb_do="240"
            	else:
            		o_espb_do =args["espb_do"]

            o_obavezni_izborni="%%"
            if "obavezni_izborni" in args:
                    o_obavezni_izborni = "%" +args["obavezni_izborni"]+"%"

            upit="SELECT * FROM `ocene` o INNER JOIN predmeti p ON o.predmet_id=p.id WHERE p.sifra LIKE %s AND p.godina_studija LIKE %s AND o.ocena>=%s AND o.ocena<=%s AND p.espb>=%s AND p.espb<=%s AND p.obavezni_izborni LIKE %s AND  student_id=%s ORDER BY "+order_by+" "+order_type
            vrednost=(
            o_sifra,
            o_godina_studija,
            o_ocena_od,
            o_ocena_do,
            o_espb_od,
            o_espb_do,
            o_obavezni_izborni,
            id
            )

            print(upit,vrednost)

            kursor.execute(upit,vrednost)
            ocene=kursor.fetchall()

            return render_template("student_pregled.html",
                student=student,
                predmeti=predmeti,
                ocene=ocene,
                rola=rola(),
                order_type=order_type,
                args=args)
    else:
        return redirect(url_for('login'))




@app.route("/student_obrisi/<id>", methods=["GET"])
def student_obrisi(id):
    if (rola() != "administrator"):
        return redirect(url_for("studenti"))
    if ulogovan():

        upit="SELECT korisnik_id FROM studenti WHERE id=%s"
        vrednost=(id,)

        kursor.execute(upit,vrednost)
        rezultat=kursor.fetchone()
        korisnik_id=rezultat.get('korisnik_id')

        upit="DELETE FROM `korisnici` WHERE id=%s"
        vrednost=(korisnik_id,)
        kursor.execute(upit,vrednost)
        konekcija.commit()

        return redirect(url_for("studenti"))
    else:
        return redirect(url_for('login'))





#---------------OCENE-----------------



@app.route("/oceni/<id>",methods=["POST"])
def oceni(id):
    if (rola() == "student"):
            return redirect(url_for("studenti"))
    if ulogovan():
        upit="INSERT INTO `ocene`( `ocena`, `datum`, `predmet_id`,`student_id`) VALUES (%s,%s,%s,%s)"
        forma=request.form
        vrednosti=(
            forma["ocena"],
            forma["datum"],
            forma["predmet"],
            id
        )
        kursor.execute(upit,vrednosti)
        konekcija.commit()


        promenaOcene(id)

        return redirect(url_for("studenti"))
    else:
        return redirect(url_for('login'))



@app.route("/ocena_izmena/<id>", methods=["GET","POST"])
def ocena_izmena(id):
    if (rola() != "administrator"):
        return redirect(url_for("studenti"))
    if ulogovan():
        if(request.method=="GET"):
            upit="SELECT * FROM `ocene` WHERE ocena_id=%s"
            vrednost=(id,)

            kursor.execute(upit,vrednost)
            ocena=kursor.fetchone()
            return render_template("ocena_izmena.html",ocena=ocena)

        if(request.method=="POST"):
            upit="UPDATE `ocene` SET ocena=%s WHERE ocena_id=%s"
            forma=request.form
            vrednosti=(
                forma["ocena"],
                id
            )
            kursor.execute(upit,vrednosti)
            konekcija.commit()

            #uzima id studenta na osnovu id ocene
            upit="SELECT student_id FROM ocene WHERE ocena_id=%s"
            vrednost=(id,)

            kursor.execute(upit,vrednost)
            rezultat=kursor.fetchone()
            student_id=rezultat.get('student_id')

            promenaOcene(student_id)

            return  redirect(url_for("student_pregled",id=student_id))
    else:
        return redirect(url_for('login'))






@app.route("/ocena_obrisi/<id>", methods=["GET"])
def ocena_obrisi(id):
    if (rola() != "administrator"):
        return redirect(url_for("studenti"))
    if ulogovan():
        #uzima id studenta na osnovu id ocene

        upit="SELECT student_id FROM ocene WHERE ocena_id=%s"
        vrednost=(id,)

        kursor.execute(upit,vrednost)
        rezultat=kursor.fetchone()
        student_id=rezultat.get('student_id')



        upit="DELETE FROM `ocene` WHERE ocena_id=%s"
        vrednost=(id,)
        kursor.execute(upit,vrednost)
        konekcija.commit()


        promenaOcene(student_id)

        return redirect(url_for("studenti"))
    else:
        return redirect(url_for('login'))



#---------------OSTALO-----------------

@app.route("/",methods=["GET","POST"])
def login():
    if(request.method=="GET"):
        return render_template("login.html")

    if(request.method=="POST"):
        forma=request.form
        upit="SELECT * FROM korisnici where email=%s"
        vrednost=(
            forma["inputEmail"],
        )
        kursor.execute(upit,vrednost)
        korisnik=kursor.fetchone()

        if(check_password_hash(korisnik["lozinka"],forma["inputLozinka"])):
            session["ulogovani_korisnik"]=str(korisnik)
            return redirect(url_for("studenti"))
        else:
            return render_template("login.html")


@app.route("/logout", methods=["GET"])
def logout():
    session.pop("ulogovani_korisnik", None)
    return redirect(url_for("login"))

@app.route("/export/<tip>")
def export(tip):
    if (rola() == "student"):
        if(tip!="ocene"):
            return redirect(url_for("studenti"))
    switch = {
        "studenti": "SELECT * FROM studenti",
        "korisnici": "SELECT * FROM korisnici",
        "predmeti": "SELECT * FROM predmeti",
        "ocene": "SELECT * FROM `ocene` INNER JOIN predmeti ON ocene.predmet_id=predmeti.id WHERE student_id=%s",
    }
    upit = switch.get(tip)

    if(tip=="ocene"):
        args = request.args.to_dict()
        id=args["id"]
        vrednost=(id,)

        kursor.execute(upit,vrednost)
        rezultat = kursor.fetchall()
    else:
        kursor.execute(upit)
        rezultat = kursor.fetchall()

    output = io.StringIO()
    writer = csv.writer(output)

    for row in rezultat:
        red = [ ]
        for value in row.values():
            red.append(str(value))
        writer.writerow(red)

    output.seek(0)

    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=" + tip +
        ".csv"},
    )





#---------------Funkcije-----------------

def promenaOcene(id):

    #Izracunava prosecnu ocenu
    upit = "SELECT AVG(ocena) AS rezultat FROM ocene WHERE student_id=%s"
    vrednost = (id,)
    kursor.execute(upit, vrednost)
    prosek_ocena = kursor.fetchone()

    #Izracunava broj ESPB
    upit = "SELECT SUM(espb) AS rezultat FROM predmeti WHERE id IN (SELECT predmet_id FROM ocene WHERE student_id=%s)"
    vrednost = (id,)
    kursor.execute(upit, vrednost)
    espb = kursor.fetchone()

    #Menja vrednosti u tabeli
    upit = "UPDATE studenti SET espb=%s, prosek_ocena=%s WHERE id=%s"
    vrednosti = (espb['rezultat'], prosek_ocena['rezultat'], id)
    kursor.execute(upit, vrednosti)
    konekcija.commit()

def ulogovan():
    if "ulogovani_korisnik" in session:
        return True
    else:
        return False


def rola():
    if ulogovan():
        return ast.literal_eval(session["ulogovani_korisnik"]).pop("rola")

def send_email(ime, prezime, email, lozinka):
    msg = Message(
        subject="Korisnički nalog",
        sender="ATVSS Evidencija studenata",
        recipients=[email],
        )
    msg.html = render_template("email.html", ime=ime, prezime=prezime,lozinka=lozinka)
    mail.send(msg)
    return "Sent"




app.run(debug=True)