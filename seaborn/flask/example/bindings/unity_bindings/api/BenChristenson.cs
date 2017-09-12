using UnityEngine;
using System;
using System.Collections;
using System.Collections.Generic;
using System.Reflection;
using System.Text;
using hg.ApiWebKit;
using hg.ApiWebKit.core.http;
using hg.ApiWebKit.faulters;
using hg.ApiWebKit.mappers;
using hg.ApiWebKit.core.attributes;
using hg.ApiWebKit.apis;

namespace demo.BenChristenson
{
	public class  BenChristenson : MonoBehaviour
	{
	    public behaviors.EchoMessageGet echoMessageGet;
        public behaviors.EchoGet echoGet;
        public behaviors.UserLoginEmailPost userLoginEmailPost;
        public behaviors.UserLogoutPost userLogoutPost;
        public behaviors.UserSignupPut userSignupPut;
        public behaviors.UserLoginPost userLoginPost;
        public behaviors.UserGet userGet;
        public behaviors.UserPost userPost;

		public virtual void Awake()
		{
            BenChristensonApiInitialize benChristensonApiInitialize = GetComponent<BenChristensonApiInitialize>();
            if (benChristensonApiInitialize.is_behaviors_created_at_startup())
            {
			    echoMessageGet = gameObject.AddComponent<behaviors.EchoMessageGet>();
                echoGet = gameObject.AddComponent<behaviors.EchoGet>();
                userLoginEmailPost = gameObject.AddComponent<behaviors.UserLoginEmailPost>();
                userLogoutPost = gameObject.AddComponent<behaviors.UserLogoutPost>();
                userSignupPut = gameObject.AddComponent<behaviors.UserSignupPut>();
                userLoginPost = gameObject.AddComponent<behaviors.UserLoginPost>();
                userGet = gameObject.AddComponent<behaviors.UserGet>();
                userPost = gameObject.AddComponent<behaviors.UserPost>();
			}
		}
	}
}


