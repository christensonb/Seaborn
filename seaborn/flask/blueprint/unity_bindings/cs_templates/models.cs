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

namespace %(namespace)s.models
{
	public class %(model)s
	{
	    %(model_declarations)s

        public override string ToString()
        {
            string ret = "%(model)s: ";
            %(arg_string)s
            return ret;
        }

        public static %(model)s Deserialize(string text, string encryption="", bool? includeLabel = null)
        {
            if (text == Crypto.NULL)
                return null;

            %(model)s ret = new %(model)s();
            Crypto crypto = new Crypto(text, encryption, includeLabel);
            %(arg_deserialize)s
            return ret;
        }

        public string Serialize(string encryption="", bool? includeLabel = null)
        {
            Crypto crypto = new Crypto("", encryption, includeLabel);
            %(arg_serialize)s
            return crypto.ToString();
        }

        public static List<string> SerializeList(List< %(model)s> objects, string encryption="", bool? includeLabel = null)
        {
            List<string> ret = new List<string>();
            foreach( %(model)s child in objects)
                ret.Add(child.Serialize(encryption, includeLabel));
            return ret;
        }

        public static List<%(model)s> DeserializeList(List<string> objects)
        {
            List<%(model)s> ret = new List<%(model)s>();
            foreach( string child in objects)
                ret.Add(%(model)s.Deserialize(child));
            return ret;
        }
	}
}


/*$$   --------- Examples ---------
using UnityEngine;
using System;

using hg.ApiWebKit.core.http;
using hg.ApiWebKit.core.attributes;
using hg.ApiWebKit.mappers;

namespace api.MechanicsOfPlay.models
{
	public class Hello
	{
	    public string key;
	    public int value;

        public override string ToString()
        {
            string ret = "Hello: ";
            ret += "key <" + key.ToString() + "> ";
            ret += "value <" + value.ToString() + ">";
            return ret;
        }

        public static Puzzle Deserialize(string text, string encryption="")
        {
            Puzzle ret = new Puzzle();
            Crypto crypto = new Crypto(text, encryption);
            ret.key = crypto.GetString();
            ret.value = crypto.GetInt();
            return ret;
        }

        public string Serialize(string encryption="")
        {
            Crypto crypto = new Crypto("", encryption);
            crypto.AddString(key);
            crypto.AddInt(value);
            return crypto.ToString();
        }


    }
}

