from app.database.mongo import db

async def get_or_create_conversation(conversation_id, user_id):
    conversation = await db["conversation"].find_one({"conversation_id": conversation_id})
    if not conversation:
        conversation = {
            "conversation_id": conversation_id,
            "user_id": user_id,
            "messages": []
        }
    return conversation

async def update_conversation(conversation_id, user_id, user_message, assistant_message_db):
    await db["conversation"].update_one(
        {"conversation_id": conversation_id},
        {
            "$set": {
                "user_id": user_id, 
                "conversation_id": conversation_id,
            },
            "$push": {
                "messages": {
                    "$each": [user_message, assistant_message_db]
                }
            }
        },
        upsert=True
    )