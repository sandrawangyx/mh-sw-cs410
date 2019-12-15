# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import boto3
import json
from ask_sdk_core.dispatch_components import (
    AbstractRequestHandler, AbstractExceptionHandler,
    AbstractRequestInterceptor, AbstractResponseInterceptor)
import ask_sdk_core.utils as ask_utils
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response
from ask_sdk.standard import StandardSkillBuilder
from alexa import data

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def invokeRecommend(userid):
    # call sagemaker endpont to get the prediction movies
    client = boto3.client('lambda')
    d = {
        "params": {
            "querystring": {
                "dataset_id": "100KDS",
                "userid": userid
            }
        }
    }
    response = client.invoke(
        FunctionName='recomendmovies',
        Payload=json.dumps(d)
    )
    response_payload = json.loads(response['Payload'].read().decode("utf-8"))
    recommendedMovies = response_payload[0:3]
    numOfRecommendations = len(recommendedMovies)
    if numOfRecommendations < 0: 
        speech = "Sorry we don't have any movies to recommend for you!"
    else:
        speech = "Here are a few movies you might like: "
        for i in range(numOfRecommendations):
            if i == numOfRecommendations - 1:
                speech += recommendedMovies[i]["movie_details"]["movie_title"]
            else:
                speech += "{}, ".format(recommendedMovies[i]["movie_details"]["movie_title"])
    # speech = speak_output.format(popular_movies[0].movie_title, popular_movies[1].movie_title,popular_movies[2].movie_title)
    return speech

def rateMovie(userid, movieid, rating):
    # save userid, movieid and rating in dynamodb
    dyndb = boto3.client('dynamodb', region_name='us-east-1')
    dyndb.put_item(
        TableName='Ratings',
        Item={
            'userId' : {'N':str(userid)},
            'movieId': {'N':str(movieid)},
            'rating': {'N':str(rating)}
        }
    )
    speech = "Thank you for your rating!"

    return speech

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Welcome to Smart Movies! What can I do for you?"

        return (
            handler_input.response_builder
            .speak(speak_output)
            .ask(speak_output)
            .set_should_end_session(False)
            .response
        )


class PopularMoviesIntentHandler(AbstractRequestHandler):
    """Handler for Popular Movies Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("PopularMoviesIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Here are a few popular movies you might like: {}, {}, {}"
        # speech = speak_output.format(popular_movies[0].movie_title, popular_movies[1].movie_title,popular_movies[2].movie_title)
        client = boto3.client('lambda')
        d = {
            "params": {
                "querystring": {
                    "dataset_id": "100KDS"
                }
            }
        }
        response = client.invoke(
            FunctionName='searchPopularMovies',
            Payload=json.dumps(d)
        )
        response_payload = json.loads(response['Payload'].read().decode("utf-8"))
        movie_titles = list(map(lambda x: x["_source"]["movietitle"], response_payload))
        speech = speak_output.format(movie_titles[0], movie_titles[1], movie_titles[2])
        return (
            handler_input.response_builder
            .speak(speech)
            # .ask("add a reprompt if you want to keep the session open for the user to respond")
            .response
        )


class RecommendMoviesIntentHandler(AbstractRequestHandler):
    """Handler for Recommend Movies Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("RecommendMoviesIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        persistence_attr = handler_input.attributes_manager.persistent_attributes
        if 'userid' in persistence_attr:
            speech = invokeRecommend(persistence_attr['userid'])
            return (
                handler_input.response_builder
                .speak(speech)
                .set_should_end_session(True)
                .response
            )
        else: 
            # make recommendation based on users history
            persistence_attr["prev_intent"] = "RecommendIntent"
            speak_output = "Before we can make proper recommendations, could you share your account id with us?"
            # speech = speak_output.format(popular_movies[0].movie_title, popular_movies[1].movie_title,popular_movies[2].movie_title)
            return (
                handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
            )

class RateMovieIntentHandler(AbstractRequestHandler):
    """Handler for Rate Movies Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("RateMovieIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        persistence_attr = handler_input.attributes_manager.persistent_attributes
        if 'userid' in persistence_attr:
            userid = persistence_attr['userid']
            slots = handler_input.request_envelope.request.intent.slots
            movieid = slots['movie_name'].resolutions.resolutions_per_authority[0].values[0].value.id
            rating = slots['rating'].value
            if movieid and rating:
                speech = rateMovie(userid, movieid, rating)
                return (
                    handler_input.response_builder
                    .speak(speech)
                    .response
                )
            else:
                speech = "Sorry, I didn't catch that. Can you repeat?"
                return (
                    handler_input.response_builder
                    .speak(speech)
                    .ask(speech)
                    .response
                )
        else: 
            persistence_attr["prev_intent"] = "RateMovieIntent"
            speak_output = "Before you rate any movies, could you share your account id with us?"
            # speech = speak_output.format(popular_movies[0].movie_title, popular_movies[1].movie_title,popular_movies[2].movie_title)
            return (
                handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
            )

class AccountIdIntentHandler(AbstractRequestHandler):
    """Handler for AccountId Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AccountIdIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        slots = handler_input.request_envelope.request.intent.slots
        accountId = slots['accountId']
        if accountId.value:
            persistence_attr = handler_input.attributes_manager.persistent_attributes
            persistence_attr["userid"] = accountId.value
            speech = ""
            endSession = False
            reprompt = ""
            if "prev_intent" in persistence_attr and persistence_attr["prev_intent"] == "RecommendIntent":
                del persistence_attr["prev_intent"]
                endSession = True
                reprompt = ""
                speech = invokeRecommend(accountId.value)
            elif "prev_intent" in persistence_attr and persistence_attr["prev_intent"] == "RateMovieIntent":
                del persistence_attr["prev_intent"]
                endSession = False
                speech = "Thank you! You can start rating now!"
                reprompt = speech
            else:
                speech = "Sorry, I didn't catch that. What can I do for you?"
                endSession = False
                reprompt = speech
            return (
                handler_input.response_builder
                .speak(speech)
                .ask(reprompt)
                .set_should_end_session(endSession)
                .response
            )
        else: 
            speak_output = "Sorry I didn't catch that. Could you share your account id with us?"
            # speech = speak_output.format(popular_movies[0].movie_title, popular_movies[1].movie_title,popular_movies[2].movie_title)
            return (
                handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
            )

class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "You can say list popular movies or recommend movies! How can I help?"

        return (
            handler_input.response_builder
            .speak(speak_output)
            .ask(speak_output)
            .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
            .speak(speak_output)
            .response
        )


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
            .speak(speak_output)
            # .ask("add a reprompt if you want to keep the session open for the user to respond")
            .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """

    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
            .speak(speak_output)
            .ask(speak_output)
            .response
        )

# ###################################################################

# ############# REQUEST / RESPONSE INTERCEPTORS #####################


class RequestLogger(AbstractRequestInterceptor):
    """Log the alexa requests."""

    def process(self, handler_input):
        # type: (HandlerInput) -> None
        logger.debug("Alexa Request: {}".format(
            handler_input.request_envelope.request))


class LoadPersistenceAttributesRequestInterceptor(AbstractRequestInterceptor):
    """Check if user is invoking skill for first time and initialize preset."""

    def process(self, handler_input):
        # type: (HandlerInput) -> None
        persistence_attr = handler_input.attributes_manager.persistent_attributes


class ResponseLogger(AbstractResponseInterceptor):
    """Log the alexa responses."""

    def process(self, handler_input, response):
        # type: (HandlerInput, Response) -> None
        logger.debug("Alexa Response: {}".format(response))


class SavePersistenceAttributesResponseInterceptor(AbstractResponseInterceptor):
    """Save persistence attributes before sending response to user."""

    def process(self, handler_input, response):
        # type: (HandlerInput, Response) -> None
        handler_input.attributes_manager.save_persistent_attributes()
# ###################################################################


sb = StandardSkillBuilder(
    table_name=data.DYNAMODB_TABLE_NAME, auto_create_table=True)

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(PopularMoviesIntentHandler())
sb.add_request_handler(RecommendMoviesIntentHandler())
sb.add_request_handler(RateMovieIntentHandler())
sb.add_request_handler(AccountIdIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
# make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers
sb.add_request_handler(IntentReflectorHandler())

sb.add_exception_handler(CatchAllExceptionHandler())


# Interceptors
sb.add_global_request_interceptor(RequestLogger())
sb.add_global_request_interceptor(
    LoadPersistenceAttributesRequestInterceptor())

sb.add_global_response_interceptor(ResponseLogger())
sb.add_global_response_interceptor(
    SavePersistenceAttributesResponseInterceptor())


handler = sb.lambda_handler()
