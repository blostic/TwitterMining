import com.mongodb.casbah.Imports._
import JSON._

import scala.io.Source._
import java.nio.charset.CodingErrorAction
import scala.io.Codec

object Preprocessor extends App {
		
	//config
	val SRC_DB_NAME = "twitter"
	val TAGGER_DB_NAME = "tagger"
	val stopwordsFile = "stopwords.csv"
	val tweetsAmount = 4
	//val tweetsFile = "tweets/twitter.english_tweet.json"
	
	//to prevent java.nio.charset.UnmappableCharacterException
	implicit val codec = Codec("UTF-8")
	codec.onMalformedInput(CodingErrorAction.REPLACE)
	codec.onUnmappableCharacter(CodingErrorAction.REPLACE)
  
	// get DB server connection
	val mongoConn = MongoConnection("localhost", 27017)

	// create a new DB and Collection if not present or use existing one
	val taggerTweets = mongoConn(TAGGER_DB_NAME)("tweets")
	val sourceTweets = mongoConn(SRC_DB_NAME)("english_tweet")

	// drop create
	if(args.length > 0 && args(0) == "drop"){
		taggerTweets.dropCollection()
		println("[INFO] Dropping before insert")
	}
	
	val stripper = new StopWordsStripper(stopwordsFile)
	
	//load json file with tweets	
	//val lines = scala.io.Source.fromURL(getClass.getResource(tweetsFile)).getLines()
	
	//get all tweets
	val lines = sourceTweets.find().limit(tweetsAmount)
	
	println("[INFO] Inserting " + tweetsAmount + " tweets...")
	for(line <- lines){
		val result =parseJSON(line.toString())
		println("\t+ " + result.tweetid.toString.toLong)
		val newTweet = MongoDBObject(("tweet_id",result.tweetid.toString.toLong), ("content",stripper.strip(result.text.toString.toLowerCase())))
		taggerTweets += newTweet
	}
	
	println("[SUCCESS] Tweets in DB: " + taggerTweets.size)
}