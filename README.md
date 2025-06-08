# mediatheque_numerique_export
> Programme Python qui permet d'exporter les films présents sur le site de la [Médiathèque numérique](mediatheque-numerique.com), dans le but d'en faire une [liste Letterboxd](https://letterboxd.com/clement_chn/list/films-sur-la-mediatheque-numerique/).

## Table des matières
* [General Information](#general-information)
  * [En français](#en-français)
  * [In English](#in-english)
* [Technologies Used](#technologies-used)
* [Usage](#usage)
* [Project Status](#project-status)
* [Contact](#contact)
* [License](#license)

## General Information
### En français
La Médiathèque numérique, site issu d'un partenariat entre UniversCiné et Arte, est un service de VOD destiné aux bibliothèques publiques, bibliothèques universitaires et aux entreprises et à leurs usagers. Il permet aux usagers de pouvoir regarder un certain nombre de films par mois parmi une sélection contenant plusieurs milliers d'œuvres.

Les différents sites externes permettent de voir la disponibilité de films, comme JustWatch ou Allociné, ne fournissent pas d'informations sur la Médiathèque numérique. L'objectif est donc d'avoir une liste sur [Letterboxd](https://letterboxd.com/), qui, une fois likée, apparaîtra directement sur les pages des films présents sur la Médiathèque numérique.

Le script `main.py` permet ainsi l'export, dans un CSV nommé `all_films.csv`, des titres français, réalisateurs et années des films de la Médiathèque numérique. Seuls les films de plus de 50&nbsp;minutes et présents dans la catégorie Cinéma du catalogue sont exportés. Le fichier CSV est ensuite importé dans Letterboxd via l'outil de création de listes. Lors du premier import, environ 2,5&nbsp;% des films n'ont pas pu être importé, principalement à cause de l'absence du titre français sur [TMDB](https://www.themoviedb.org/) et donc Letterboxd, ou de l'absence même du film. Vous pouvez trouver la liste letterboxd via ce lien : https://letterboxd.com/clement_chn/list/films-sur-la-mediatheque-numerique/.

### In English
The Médiathèque Numérique, a platform resulting from a partnership between UniversCiné and Arte, is a French VOD service aimed at public libraries, university libraries, companies, and their users. It allows users to watch a certain number of films per month from a selection of several thousand titles.

External sites such as JustWatch or Allociné, which show film availability, do not provide information about the Médiathèque Numérique. The goal, therefore, is to create a list on [Letterboxd](https://letterboxd.com/) which, once liked, will appear directly on the film pages for those available on the Médiathèque Numérique.

The `main.py` script enables the export of French titles, directors, and release years of films from the Médiathèque Numérique into a CSV file named `all_films.csv`. Only films longer than 50&nbsp;minutes and listed under the Cinema category of the catalog are exported. The CSV file is then imported into Letterboxd using the list creation tool. During the initial import, approximately 2.5% of the films could not be imported, mainly due to the absence of the French title on [TMDB](https://www.themoviedb.org/), and thus on Letterboxd, or the film not being available at all. You can find the Letterboxd list via this link: https://letterboxd.com/clement_chn/list/films-sur-la-mediatheque-numerique/.

## Technologies Used
- **Python** - version 3.12.2  
  - Python libraries: pandas, requests, and more (see `requirements.txt` for the full list).

## Usage
### Setup
**Ensure you have Python 3.x installed.**

**Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application
To update the CSV file, navigate to your project folder in the command prompt (with `cd` command) and run:
   ```bash
   python main.py
   ```

Or just run main.py in your IDE.


## Project Status
Project is: _complete_ - version 1.0.0.


## Contact
Created by [@cchenu](https://github.com/cchenu/) - feel free to contact me!

## License
This project is open source and available under the [MIT License](LICENSE).

