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
    char* data;
} game_packet;

/**
 * @brief Transforms a game_packet structure into a packet which is
 * an array of bytes (unsigned char*) * 
 * 
 * @param g the game packet we want to serialize
 * @return char* the serialized bytes array
 */
char* serialize_packet(game_packet g);

/**
 * @brief Transforms a serialized packet back to a structure
 * game_packet and returns it
 * 
 * @param s_packet the serialized bytes array
 * @return game_packet the game packet de-serialized
 */
game_packet deserialize_packet(unsigned char *s_packet);



#endif 