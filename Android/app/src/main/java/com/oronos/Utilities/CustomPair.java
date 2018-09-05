package com.oronos.Utilities;

import java.util.Map;

/*
 * Cette classe generique represente une paire de valeur.
 */
public class CustomPair<K, V> implements Map.Entry<K, V> {

    private final K key;
    private V value;

    /*
     * Constructeur de la classe.
     */
    public CustomPair(K key, V value) {
        this.key = key;
        this.value = value;
    }

    /*
     * Getter sur l'attribut Key. La clef ici contiendra les messages du serveur
     * vers le client.
     */
    public K getKey() {
        return key;
    }

    /*
     * Getter sur l'attribut Value. Cette attribut contiendra les resultats du
     * serveur, comme les fichiers a envoyer.
     */
    public V getValue() {
        return value;
    }

    /*
     * Setter sur l'attribut Value.
     */
    public V setValue(V value) {
        V oldValue = this.value;
        this.value = value;
        return oldValue;
    }
}