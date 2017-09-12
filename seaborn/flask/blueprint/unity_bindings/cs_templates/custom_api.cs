/*
    This code is placeholder code for the developer to modify so as to call the rest call with
    parameters and to assign the callback function.

    So remove the placeholder in the namespace and modify to your hearts content

    This should be added to the REST game object.
*/

using UnityEngine;
using UnityEngine.UI;
using System;
using %(namespace)s;
using hg.ApiWebKit;
using hg.ApiWebKit.core.http;
using %(namespace)s.operations;
using System.Collections.Generic;

namespace %(namespace)s.placeholder
{
	public class %(short_namespace)sCustomApi : MonoBehaviour
	{
	    private static %(short_namespace)sCustomApi m_instance = null;
		private static %(short_namespace)s %(short_namespace_instance)s = null;
		private static %(short_namespace)sApiInitialize %(short_namespace_instance)sApiInitialize = null;
        public static int m_logLevel=1; // 0: no logging, 1: log on response error, 2: log on api errors, 3: log on error and success, 4: log on sent error and success
        %(class_members)s

		public void Awake()
		{
            m_instance = this;
			%(short_namespace_instance)s = GetComponent<%(short_namespace)s> ();
			%(short_namespace_instance)sApiInitialize = GetComponent<%(short_namespace)sApiInitialize> ();
		}

        public static %(short_namespace)sCustomApi Instance()
        {
            return m_instance;
        }

        public static string Prefix()
        {
            return Seaborn.Timestamp.Millisecond() + " API ";
        }

        /* Endpoint Code Here */

        public static void %(name)s(%(custom_arguments)s
        {   %(function_description)s
            if (%(short_namespace_instance)s.%(name_instance)s == null){
                %(short_namespace_instance)s.%(name_instance)s = m_instance.gameObject.AddComponent<behaviors.%(name)s>();
                %(short_namespace_instance)s.%(name_instance)s.DestroyOnComplete = %(short_namespace_instance)sApiInitialize.is_behavior_destroyed_on_complete();
            }

            %(null_list)s
            if(m_logLevel>3)
                Debug.Log(Prefix()+"%(name)s started");

            %(short_namespace_instance)s.%(name_instance)s.Spawn(%(arg_params_with_comma)s
                                       Callback: new Action<operations.%(name)s, HttpResponse> ((operation, response) =>
            {
                try
                {
                    if (response.HasError)
                    {
                        if(m_logLevel>1)
                            Debug.LogError(Prefix()+"%(name)s failed " + response.Error);
                    }
                    else
                    {
                        %(response_type)s responseData = operation.responseData; %(response_desc)s
                        if(m_logLevel>2)
                            Debug.Log(Prefix()+"%(name)s completed Successfully with " + %(response_str)s);
                    }
                }
                catch (Exception ex)
                {
                    if(m_logLevel>0)
                        Debug.LogError(Prefix()+"%(name)s failed in response with: "+ex.ToString());
                }
            }));
        }
        /* Endpoint Code Here */
    }
}


/*$$   --------- Examples ---------
using UnityEngine;
using System;
using api.MechanicsOfPlay;
using hg.ApiWebKit.core.http;
using api.MechanicsOfPlay.operations;

namespace api.MechanicsOfPlay
{
	public class  PasswordRest : MonoBehaviour
	{
		private MechanicsOfPlay mechanicsOfPlay;

		public void Start()
		{
			mechanicsOfPlay = GetComponent<MechanicsOfPlay> ();
		}

		public void HelloEchoGet()
		{   // This call will simply echo your message back to you

            // optional parameters
            string message = "Hello"; // this is the message I will echo back

            mechanicsOfPlay.helloEchoGet.Spawn(message,
			                                   OnComplete: new Action<operations.HelloEchoGet, HttpResponse> ((operation, response) =>
                {
                    if (response.HasError)
                    {
                        Debug.Log("Hello Echo Get failed " + response.Error);
                    }
                    else
                    {
                        string responseData = operation.responseData;
                        Debug.Log("Hello Echo Get completed Successfully with " + responseData.ToString());
                    }
				}));
		}

		public void HelloWaitGet()
		{   // This call will wait to test calls that are not instantaneous

            // optional parameters
            int seconds = 5; // this is the number of seconds to wait before returning
			mechanicsOfPlay.helloWaitGet.Spawn(seconds,
			                                   OnComplete: new Action<operations.HelloWaitGet, HttpResponse> ((operation, response) =>
	        	{
                    if (response.HasError)
                    {
                        Debug.Log("Hello Echo Get failed " + response.Error);
                    }
                    else
                    {
                        string responseData = operation.responseData;
                        Debug.Log("Hello Echo Get completed Successfully with " + responseData.ToString());
                    }
				}));
		}

        public void HelloKeyGet()
        {   // This call will wait to test calls that are not instantaneous

            // optional parameters
            string key = "hello"; // this is the key the value will be stored under
            mechanicsOfPlay.helloKeyGet.Spawn(key,
                                               OnComplete: new Action<operations.HelloKeyGet, HttpResponse>((operation, response) =>
                                               {
                                                   if (response.HasError)
                                                   {
                                                       Debug.Log("Hello Key Get failed " + response.Error);
                                                   }
                                                   else
                                                   {
                                                       api.MechanicsOfPlay.models.Hello responseData = operation.responseData;
                                                       Debug.Log("Hello Key Get completed Successfully with " + responseData.ToString());
                                                   }
                                               }));
        }

        public void HelloKeyPut()
        {   // This call will wait to test calls that are not instantaneous

            // optional parameters
            string key = "hello"; // this is the key the value will be stored under
            string value = "world"; // this is the value to be stored
            mechanicsOfPlay.helloKeyPut.Spawn(key, value,
                                               OnComplete: new Action<operations.HelloKeyPut, HttpResponse>((operation, response) =>
                                               {
                                                   if (response.HasError)
                                                   {
                                                       Debug.Log("Hello Key Put failed " + response.Error);
                                                   }
                                                   else
                                                   {
                                                       api.MechanicsOfPlay.models.Hello responseData = operation.responseData;
                                                       Debug.Log("Hello Key Put completed Successfully with " + responseData.ToString());
                                                   }
                                               }));
        }
    }
}
/*