### Koparka Tweetów
#### Niezbędne biblioteki

##### Twython
Biblioteka do Twitter API: *Twython* - https://twython.readthedocs.org/en/latest/index.html

Opis użycia Streaming API w Twythonie: https://twython.readthedocs.org/en/latest/usage/streaming_api.html

Instalacja Twythona:

    $ sudo apt-get install pip
    $ sudo pip install twython

##### Mongoengine:

    $ sudo apt-get install python-mongoengine

####Użycie

Koparka tweetów została napisana w modelu klient-server, dzięki czemu mamy możliwość kopania tweetów w środowisku rozproszonym. 

##### Serwer
Proces serwera odpala się poprzez wpisanie w terminalu komendy:

    $ python server.py -f twitter.config
    
Gdzie opcja -f umożliwia wczytanie pliku konfiguracyjnego.

Zgodnie z sugestią, dostarczyliśmy 2 pliki konfiguracyjne:

 - twitter.whole-world.config - umożliwia kopanie tweetów z terenu całego świata

 - twitter.config - umożliwia kopanie tweetów tylko z terenu Krakowa

Aby zapoznać się z formatem pliku konfiguracyjnego, jak również z opcjami uruchomienia servera, należy wpisać w konsoli:


    $ python server.py -h

##### Klient
Proces klienta odpalamy poprzez wpisanie:

	$ client.py [ -v ] server_host server_port [ auth_file ]


###Wyświetlanie tweetów

#####Potrzebujemy:

 - MongoDB 2.4.9 ( jest prawdopodobieństwo, że na innych wersjach nie zadziała)
    http://downloads.mongodb.org/linux/mongodb-linux-x86_64-2.4.9.tgz
 - Elasticsearch 1.0.0
    https://download.elasticsearch.org/elasticsearch/elasticsearch/elasticsearch-1.0.0.tar.gz

Możemy je odpalać prosto z katalogów, które wypakujemy.

Załóżmy, że chcemy wyświetlać tweety, które znajdują się w bazie lokalnej 'twitter' i kolekcji 'generic_tweet'.

#####Konfiguracja Mongo:

1. Odpalalamy mongo jako replikę

        $ sudo ./mongod --replSet "rs0"
2. Łączymy się z bazą

        $ ./mongo
3. Potem w terminalu 

        $ use twitter
        $ rs.initiate()
        

#####Konfiguracja Elasticsearch:

1. Bedąc w głównym katalogu pobieramy potrzebne wtyczki:

        $ ./bin/plugin -install elasticsearch/elasticsearch-mapper-attachments/1.9.0
        $ ./bin/plugin --install com.github.richardwilly98.elasticsearch/elasticsearch-river-mongodb/2.0.0
        $ ./bin/plugin --url https://github.com/triforkams/geohash-facet/releases/download/geohash-facet-0.0.14/geohash-facet-0.0.14.jar --install geohash-facet
2. Uruchamiamy Elasticsearch

        $ ./bin/elasticsearch
3. Teraz konfiguracja: 

        $ curl -XPUT 'localhost:9200/twitter' -d '{
            "mappings": {
              "generic_tweet" : {
                "properties" : {
                  "_cls" : {
                    "type" : "string"
                  },
                  "_types" : {
                    "type" : "string"
                  },
                  "description" : {
                    "type" : "string"
                  },
                  "geo" : {
                    "type" : "double"
                  },
                  "geohash" : {
                    "type" : "string"
                  },
                  "location" : {
                    "type" : "geo_point"
                  },
                  "text" : {
                    "type" : "string"
                  },
                  "tweetid" : {
                    "type" : "long"
                  },
                  "userid" : {
                    "type" : "long"
                  },
                  "tags" : {
                  	"type" : "string"
                  }
                }
              }
            }
          }'
        $ curl -XPUT 'localhost:9200/_river/twitter/_meta' -d '{ 
            "type": "mongodb", 
            "mongodb": { 
                "db": "twitter", 
                "collection": "generic_tweet"
            }, 
            "index": {
                "name": "twitter", 
                "type": "generic_tweet" 
            }
        }'
4. Po wykonaniu powyższych komend utworzyliśmy indeks o nazwie 'twitter' z elementami o typie 'generic_tweet', które pobieramy z lokalnej bazy 'twitter' i kolekcji 'generic_tweet'.
5. Restatrujemy Elasticrearch. Aby sprawdzić czy wszystko działa wpisujemy w przegladarke:

        $ http://localhost:9200/twitter/_search?search_type=count&pretty=1
6. Jeśli otrzymaliśmy JSONa z odpowiedzią, gdzie klucz "total" jest rózny od zera to prawdopodobnie wszystko jest ok.
    

    
###Tagger

#####Potrzebujemy:
- Wymagania takie same jak przy wyświetlaniu tweetów (running elasticsearch i mongo).
Elasticsearch skonfigurowany jak wyżej.
Obecna implementacja zakłada że elasticsearch jest dostępny na 127.0.0.1:9200, natomiast mongo na 127.0.0.1:27017

- Scala + sbt

#####Wersje:
W repo znajdują sie dwie wersje taggera: podstawowa (Python) oraz rozszerzona (Scala).
 
- Podstawowa (Python): taguje tweety na podstawie dostarczonych plików z wcześniej zdefiniowanymi tagami. W metodzie każdy tweet jest sprawdzany czy zawiera kluczowe słowa wymienione we wspomnianych plikach. Jeśli tak, przypisuje mu tagi odpowiednie dla tych słów kluczowych.
- Rozszerzona (Scala): machine learning. Wykorzystuje bibliotekę MLlib Apache Spark. Z założenia metoda ta miała polegać na wielokrotnej klasyfikacji binarnej. W repozytorium znajduje się implementacja realizująca pojedynczą klasyfikację binarną. Niestety nie zachowuje się ona zgodnie z oczekiwaniami. Należałoby odnaleźć błąd, jaki się wkradł podczas implementowania.

#####Uruchomienie
- Podstawowa: 

++ console: 
        
        $ python tag_parser.py [ścieżki do plików z tagami]
++ gui: 
    
        $ python simple_tagger_gui.py

- Rozszerzona:
<br>W folderze 'tagger' znajduje się plik budujący sbt. W tym folderze wołamy:

        $ sbt run
i wybieramy w zalężności od potrzeb Preprocessor albo Tagger. Preprocessor tworzy bazę na potrzeby taggera i przerzuca do niej odpowiednio sparsowane tweety. Tagger jest właściwą częścią, reliazującą tagowanie tweetów.
