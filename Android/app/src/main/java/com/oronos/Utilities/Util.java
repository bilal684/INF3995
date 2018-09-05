package com.oronos.Utilities;

import org.w3c.dom.Node;
import org.w3c.dom.NodeList;

/*
* Cette classe est une classe utilitaire, elle contient des fonctions à usages générales
* */
public class Util {

    public static class Utilities
    {
        /*
        * Méthode permettant de vérifier si un tabcontainer est vide. Cette méthode est utilisée lors de la construction de la vue.
        * */
        public static boolean checkIfTabContainerHasNonEmptyChilds(Node element)
        {
            boolean hasChilds = false;
            NodeList childs = element.getChildNodes();
            for(int i = 0; i < childs.getLength(); i++)
            {
                if(childs.item(i).getNodeType() == Node.ELEMENT_NODE)
                {
                    hasChilds = true;
                    break;
                }
            }
            return hasChilds;
        }
    }
}
