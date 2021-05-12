#ifndef SERIALIZATION
#define SERIALIZATION

/**
 * @brief Game packet structure with (more details on usage at the end of file):
 * player_id : number of the player who sent the packet 
 * action : the action the player did (see here for more informations : shorturl.at/kAGN7)
 * data : string containing action, semicolon separated
 */
typedef struct
{
    int player_id;
    int action;
    char *data;
} game_packet;

/**
 * @brief Transforms a game_packet structure into a packet which is
 * an array of bytes (unsigned char*) * 
 * 
 * @param g the game packet we want to serialize
 * @return char* the serialized bytes array
 */
unsigned char *serialize_packet(game_packet g);

/**
 * @brief Transforms a serialized packet back to a structure
 * game_packet and returns it
 * 
 * @param s_packet the serialized bytes array
 * @return game_packet the game packet de-serialized
 */
game_packet deserialize_packet(unsigned char *s_packet);

/*
    Game packets index
    ------------------

    -----------------------------
    | player_id | action | data |
    -----------------------------

    --
    "player_id": a number between 0 and the maximum possible players, which acts as an identifier for the player 
    --
    "action" : a number which represent an action, exterior the game (0;3), in-game (3;)
        -> 0 : First connection of a player 
        -> 1 : Game data for those who connect or if we need to update the game state for everyone (not sure of what would be in the data yet)
        -> 2 : IP + Port + id packet
        -> 3 : Disconnect packet, with IP+Port in data
        -> 4 : Move packet 
        -> 5 : Attack packet 
        -> 6 : Open chest
        -> 7 : Chatting
        -> 8 : Move ennemies
        -> 9 : Attack ennemies
        -> 10 : Change ID
        -> 11 : maybe more in the future...
    --
    "data" : this string contains the action of the player, different for each value of action. It may contain IPs, movements instructions...
    --  
*/

#endif