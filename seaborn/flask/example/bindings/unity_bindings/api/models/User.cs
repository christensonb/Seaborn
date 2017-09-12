/*
    This file contains models classes that the json response data will be mapped to
*/

using UnityEngine;
using System;
using System.Collections.Generic;
using hg.ApiWebKit.core.http;
using hg.ApiWebKit.core.attributes;
using hg.ApiWebKit.mappers;
using Seaborn;

namespace demo.BenChristenson.models
{
	public class User
	{
	    public int user_id;
        public string username;
        public string email;
        public string full_name;

        public override string ToString()
        {
            string ret = "User: ";
            ret += "user_id <'"+user_id.ToString()+"'> ";
            return ret;
        }

        public static User Deserialize(string text, string encryption="", bool? includeLabel = null)
        {
            if (text == Crypto.NULL)
                return null;

            User ret = new User();
            Crypto crypto = new Crypto(text, encryption, includeLabel);
            ret.user_id = crypto.GetInt();
            ret.username = crypto.GetString();
            ret.email = crypto.GetString();
            ret.full_name = crypto.GetString();
            return ret;
        }

        public string Serialize(string encryption="", bool? includeLabel = null)
        {
            Crypto crypto = new Crypto("", encryption, includeLabel);
            crypto.AddInt(user_id,"user_id");
            crypto.AddString(username,"username");
            crypto.AddString(email,"email");
            crypto.AddString(full_name,"full_name");
            return crypto.ToString();
        }

        public static List<string> SerializeList(List< User> objects, string encryption="", bool? includeLabel = null)
        {
            List<string> ret = new List<string>();
            foreach( User child in objects)
                ret.Add(child.Serialize(encryption, includeLabel));
            return ret;
        }

        public static List<User> DeserializeList(List<string> objects)
        {
            List<User> ret = new List<User>();
            foreach( string child in objects)
                ret.Add(User.Deserialize(child));
            return ret;
        }
	}
}


