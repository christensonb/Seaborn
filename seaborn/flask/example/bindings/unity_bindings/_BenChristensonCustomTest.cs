/*
    This code is placeholder code for the developer to modify so as to call the rest call with
    parameters and to assign the callback function.

    So remove the placeholder in the namespace and modify to your hearts content

    This should be added to the REST game object.
*/

using UnityEngine;
using UnityEngine.UI;
using System;
using demo.BenChristenson;
using hg.ApiWebKit;
using hg.ApiWebKit.core.http;
using demo.BenChristenson.operations;
using System.Collections.Generic;

namespace demo.BenChristenson.placeholder
{
	public class BenChristensonCustomTest : MonoBehaviour
	{
	    private static BenChristensonCustomTest m_instance = null;
		private static BenChristenson benChristenson = null;
		private static BenChristensonApiInitialize benChristensonApiInitialize = null;
        public static int m_logLevel=1; // 0: no logging, 1: log on response error, 2: log on api errors, 3: log on error and success, 4: log on sent error and success
        

		public void Awake()
		{
            m_instance = this;
			benChristenson = GetComponent<BenChristenson> ();
			benChristensonApiInitialize = GetComponent<BenChristensonApiInitialize> ();
		}

        public static BenChristensonCustomTest Instance()
        {
            return m_instance;
        }

        public static string Prefix()
        {
            return Seaborn.Timestamp.Millisecond() + " API ";
        }

        

        public static void EchoMessageGet(
            string message = "hello")               // str of the message to echo
        {   /*
			Very simple endpoint that just echos your message back to you
			*/
            if (benChristenson.echoMessageGet == null){
                benChristenson.echoMessageGet = m_instance.gameObject.AddComponent<behaviors.EchoMessageGet>();
                benChristenson.echoMessageGet.DestroyOnComplete = benChristensonApiInitialize.is_behavior_destroyed_on_complete();
            }

            
            if(m_logLevel>3)
                Debug.Log(Prefix()+"EchoMessageGet started");

            benChristenson.echoMessageGet.Spawn(message, 
                                       Callback: new Action<operations.EchoMessageGet, HttpResponse> ((operation, response) =>
            {
                try
                {
                    if (response.HasError)
                    {
                        if(m_logLevel>1)
                            Debug.LogError(Prefix()+"EchoMessageGet failed " + response.Error);
                    }
                    else
                    {
                        string responseData = operation.responseData;             // str of the message echoed
                        if(m_logLevel>2)
                            Debug.Log(Prefix()+"EchoMessageGet completed Successfully with " + responseData.ToString());
                    }
                }
                catch (Exception ex)
                {
                    if(m_logLevel>0)
                        Debug.LogError(Prefix()+"EchoMessageGet failed in response with: "+ex.ToString());
                }
            }));
        }
        

        public static void EchoGet()
        {   /*
			This will return the string "Hello World!"
			*/
            if (benChristenson.echoGet == null){
                benChristenson.echoGet = m_instance.gameObject.AddComponent<behaviors.EchoGet>();
                benChristenson.echoGet.DestroyOnComplete = benChristensonApiInitialize.is_behavior_destroyed_on_complete();
            }

            
            if(m_logLevel>3)
                Debug.Log(Prefix()+"EchoGet started");

            benChristenson.echoGet.Spawn(
                                       Callback: new Action<operations.EchoGet, HttpResponse> ((operation, response) =>
            {
                try
                {
                    if (response.HasError)
                    {
                        if(m_logLevel>1)
                            Debug.LogError(Prefix()+"EchoGet failed " + response.Error);
                    }
                    else
                    {
                        string responseData = operation.responseData;             // str of "Hello World!"
                        if(m_logLevel>2)
                            Debug.Log(Prefix()+"EchoGet completed Successfully with " + responseData.ToString());
                    }
                }
                catch (Exception ex)
                {
                    if(m_logLevel>0)
                        Debug.LogError(Prefix()+"EchoGet failed in response with: "+ex.ToString());
                }
            }));
        }
        

        public static void UserLoginEmailPost(
            string email,                           // str of the email as an alternative to username
            string password)                        // str of the password
        {   /*
			This will process logging the user in
			*/
            if (benChristenson.userLoginEmailPost == null){
                benChristenson.userLoginEmailPost = m_instance.gameObject.AddComponent<behaviors.UserLoginEmailPost>();
                benChristenson.userLoginEmailPost.DestroyOnComplete = benChristensonApiInitialize.is_behavior_destroyed_on_complete();
            }

            
            if(m_logLevel>3)
                Debug.Log(Prefix()+"UserLoginEmailPost started");

            benChristenson.userLoginEmailPost.Spawn(email, password, 
                                       Callback: new Action<operations.UserLoginEmailPost, HttpResponse> ((operation, response) =>
            {
                try
                {
                    if (response.HasError)
                    {
                        if(m_logLevel>1)
                            Debug.LogError(Prefix()+"UserLoginEmailPost failed " + response.Error);
                    }
                    else
                    {
                        models.User responseData = operation.responseData;        // User dict
                        if(m_logLevel>2)
                            Debug.Log(Prefix()+"UserLoginEmailPost completed Successfully with " + responseData.ToString());
                    }
                }
                catch (Exception ex)
                {
                    if(m_logLevel>0)
                        Debug.LogError(Prefix()+"UserLoginEmailPost failed in response with: "+ex.ToString());
                }
            }));
        }
        

        public static void UserLogoutPost()
        {   /*
			This will log the user out
			*/
            if (benChristenson.userLogoutPost == null){
                benChristenson.userLogoutPost = m_instance.gameObject.AddComponent<behaviors.UserLogoutPost>();
                benChristenson.userLogoutPost.DestroyOnComplete = benChristensonApiInitialize.is_behavior_destroyed_on_complete();
            }

            
            if(m_logLevel>3)
                Debug.Log(Prefix()+"UserLogoutPost started");

            benChristenson.userLogoutPost.Spawn(
                                       Callback: new Action<operations.UserLogoutPost, HttpResponse> ((operation, response) =>
            {
                try
                {
                    if (response.HasError)
                    {
                        if(m_logLevel>1)
                            Debug.LogError(Prefix()+"UserLogoutPost failed " + response.Error);
                    }
                    else
                    {
                        string responseData = operation.responseData;             // str of a message saying success
                        if(m_logLevel>2)
                            Debug.Log(Prefix()+"UserLogoutPost completed Successfully with " + responseData.ToString());
                    }
                }
                catch (Exception ex)
                {
                    if(m_logLevel>0)
                        Debug.LogError(Prefix()+"UserLogoutPost failed in response with: "+ex.ToString());
                }
            }));
        }
        

        public static void UserSignupPut(
            string username,                        // str of the username give my the player
            string password,                        // str of the password which will be hashed
            string email = null,                    // str of the user's email address
            string full_name = null)                // str of the full name
        {   /*
			This will create a PnP user
			*/
            if (benChristenson.userSignupPut == null){
                benChristenson.userSignupPut = m_instance.gameObject.AddComponent<behaviors.UserSignupPut>();
                benChristenson.userSignupPut.DestroyOnComplete = benChristensonApiInitialize.is_behavior_destroyed_on_complete();
            }

            
            if(m_logLevel>3)
                Debug.Log(Prefix()+"UserSignupPut started");

            benChristenson.userSignupPut.Spawn(username, password, email, full_name, 
                                       Callback: new Action<operations.UserSignupPut, HttpResponse> ((operation, response) =>
            {
                try
                {
                    if (response.HasError)
                    {
                        if(m_logLevel>1)
                            Debug.LogError(Prefix()+"UserSignupPut failed " + response.Error);
                    }
                    else
                    {
                        models.User responseData = operation.responseData;        // User dict of the user created
                        if(m_logLevel>2)
                            Debug.Log(Prefix()+"UserSignupPut completed Successfully with " + responseData.ToString());
                    }
                }
                catch (Exception ex)
                {
                    if(m_logLevel>0)
                        Debug.LogError(Prefix()+"UserSignupPut failed in response with: "+ex.ToString());
                }
            }));
        }
        

        public static void UserLoginPost(
            string username,                        // str of the username
            string password,                        // str of the password
            string email = null)                    // str of the email as an alternative to username
        {   /*
			This will process logging the user in
			*/
            if (benChristenson.userLoginPost == null){
                benChristenson.userLoginPost = m_instance.gameObject.AddComponent<behaviors.UserLoginPost>();
                benChristenson.userLoginPost.DestroyOnComplete = benChristensonApiInitialize.is_behavior_destroyed_on_complete();
            }

            
            if(m_logLevel>3)
                Debug.Log(Prefix()+"UserLoginPost started");

            benChristenson.userLoginPost.Spawn(username, password, email, 
                                       Callback: new Action<operations.UserLoginPost, HttpResponse> ((operation, response) =>
            {
                try
                {
                    if (response.HasError)
                    {
                        if(m_logLevel>1)
                            Debug.LogError(Prefix()+"UserLoginPost failed " + response.Error);
                    }
                    else
                    {
                        models.User responseData = operation.responseData;        // User dict
                        if(m_logLevel>2)
                            Debug.Log(Prefix()+"UserLoginPost completed Successfully with " + responseData.ToString());
                    }
                }
                catch (Exception ex)
                {
                    if(m_logLevel>0)
                        Debug.LogError(Prefix()+"UserLoginPost failed in response with: "+ex.ToString());
                }
            }));
        }
        

        public static void UserGet()
        {   
            if (benChristenson.userGet == null){
                benChristenson.userGet = m_instance.gameObject.AddComponent<behaviors.UserGet>();
                benChristenson.userGet.DestroyOnComplete = benChristensonApiInitialize.is_behavior_destroyed_on_complete();
            }

            
            if(m_logLevel>3)
                Debug.Log(Prefix()+"UserGet started");

            benChristenson.userGet.Spawn(
                                       Callback: new Action<operations.UserGet, HttpResponse> ((operation, response) =>
            {
                try
                {
                    if (response.HasError)
                    {
                        if(m_logLevel>1)
                            Debug.LogError(Prefix()+"UserGet failed " + response.Error);
                    }
                    else
                    {
                        models.User responseData = operation.responseData;        // User dict of the current user
                        if(m_logLevel>2)
                            Debug.Log(Prefix()+"UserGet completed Successfully with " + responseData.ToString());
                    }
                }
                catch (Exception ex)
                {
                    if(m_logLevel>0)
                        Debug.LogError(Prefix()+"UserGet failed in response with: "+ex.ToString());
                }
            }));
        }
        

        public static void UserPost(
            string username = null,                 // str of the username give my the player
            string email = null,                    // str of the user's email address
            string full_name = null,                // str of the full name
            string password = null)                 // str of the password which will be hashed
        {   /*
			This will update a PnP user
			*/
            if (benChristenson.userPost == null){
                benChristenson.userPost = m_instance.gameObject.AddComponent<behaviors.UserPost>();
                benChristenson.userPost.DestroyOnComplete = benChristensonApiInitialize.is_behavior_destroyed_on_complete();
            }

            
            if(m_logLevel>3)
                Debug.Log(Prefix()+"UserPost started");

            benChristenson.userPost.Spawn(username, email, full_name, password, 
                                       Callback: new Action<operations.UserPost, HttpResponse> ((operation, response) =>
            {
                try
                {
                    if (response.HasError)
                    {
                        if(m_logLevel>1)
                            Debug.LogError(Prefix()+"UserPost failed " + response.Error);
                    }
                    else
                    {
                        models.User responseData = operation.responseData;        // User dict of the user updated
                        if(m_logLevel>2)
                            Debug.Log(Prefix()+"UserPost completed Successfully with " + responseData.ToString());
                    }
                }
                catch (Exception ex)
                {
                    if(m_logLevel>0)
                        Debug.LogError(Prefix()+"UserPost failed in response with: "+ex.ToString());
                }
            }));
        }
        
    }
}


