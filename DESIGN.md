Project groepje 16

Alle routes
login (GET, POST)
    return timeline
logout (GET) (geen scherm)
    return general homepage
register (GET, POST)
    return timeline
change password (GET, POST)
    return timeline
general homepage (GET, POST). Dit is de homepage voor de niet ingelogde gebruikers. Vanaf hier wordt een user doorgestuurd naar de login of register page.
    return log in
    return register
    return search
timeline (GET, POST). Dit is de homepage voor de ingelogde gebruiker, dus hun timeline. Hier zien de gebruikers de afspeellijsten die zij volgen. Bovenaan komen dan de afspeellijsten die waar als laatst een nummer aan is toegevoegd.
    return create
    return group profile
    return search
create (GET, POST). Dit is de pagina waar een nieuwe groep/afspeellijst gemaakt kan worden.
    return group profile
group profile (GET, POST). Dit is de pagina waar het profiel van de groep wordt weergegeven. Dus bijvoorbeeld de groepsnaam en misschien een kleine beschrijving. Bovendien staan hier de nummers van de afspeellijst. Vanaf hier kunnen gebruikers ook de afspeellijst gaan volgen en ingelogde gebruikers kunnen een nummer toevoegen aan de afspeellijst.
    return add number
following (GET) (geen scherm). Deze route zorgt ervoor dat een user een groep gaat volgen en dat dus deze informatie wordt opgeslagen in de database.
    return group profile
add number  (GET, POST).  Alle mensen die zijn toegevoegd aan een groep mogen nummers toevoegen aan de afspeellijst.
    return group profile
search (GET, POST). Dit is een zoekpagina waarin je naar groepen kan zoeken.
    return results
results (GET, POST). Dit zijn de resultaten van de zoekpagina. Gebaseerd op de users input van de zoekpagina.
    return group profile

Helpers functies
In helpers hebben we een functie die van de link de YouTube video key pakt en hem in de database op slaat

Views
In de afbeelding DESIGN staan de views met bijbehorende links