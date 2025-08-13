from dotenv import load_dotenv
from sqlalchemy.orm import Session

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from core.prompts import STORY_PROMPT
from models.story import Story, StoryNode
from core.models import StoryLLMResponse, StoryNodeLLM



load_dotenv()


class StoryGenerator:
    """
    Class to generate a choose-your-own-adventure story using a language model.
    """
    @classmethod
    def _get_llm(cls):
        """
        Initializes and returns the language model instance.
        """
        return ChatOpenAI(
            model='gpt-4o-mini',
        )
    
    @classmethod
    def generate_story(
        cls,
        db: Session,
        session_id: str,
        theme: str = 'fantacy'
        ) -> Story:
        """
        Generates a story based on the provided theme.
        Args:
            db (Session): Database session for saving the story.
            session_id (str): Unique identifier for the session.
            theme (str): Theme of the story to be generated.
        Returns:
            Story: The generated story object.
        """
        llm = cls._get_llm()
        story_parser = PydanticOutputParser(pydantic_object=StoryLLMResponse)
        # Create the prompt with the theme
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    STORY_PROMPT
                ),
                (
                    'human',
                    f'Create the story with the theme: {theme}.'
                )
            ]
        ).partial(format_instructions=story_parser.get_format_instructions())

        raw_response = llm.invoke(prompt.invoke({}))

        # Parse the response into a StoryLLMResponse object
        response_text = raw_response
        if hasattr(raw_response, 'content'):
            response_text = raw_response.content

        story_structure = story_parser.parse(response_text)

        story_db = Story(
            title=story_structure.title,
            session_id=session_id,
        )
        db.add(story_db)
        db.flush()

        root_node_data = story_structure.rootNode
        if isinstance(root_node_data, dict):
            root_node_data = StoryNodeLLM.model_validate(root_node_data)

        cls._process_story_node(db, story_db.id, root_node_data, is_root=True)

        db.commit()
        return story_db

    @classmethod
    def _process_story_node(
        cls,
        db: Session,
        story_id: int,
        node_data: StoryNodeLLM,
        is_root: bool = False
    ) -> StoryNode:
        """
        Processes a story node and saves it to the database.
        Args:
            db (Session): Database session for saving the node.
            story_id (int): ID of the story to which the node belongs.
            node_data (StoryNodeLLM): The node data to be processed.
            is_root (bool): Whether this node is the root node.
        """
        node = StoryNode(
            story_id=story_id,

            content=node_data.content if hasattr(
                node_data,
                'content'
            ) else node_data['content'],

            is_root=is_root,

            is_ending=node_data.isEnding if hasattr(
                node_data,
                'isEnding'
            ) else node_data['isEnding'],

            is_winning_ending=node_data.isWinningEnding if hasattr(
                node_data,
                'isWinningEnding'
            ) else node_data['isWinningEnding'],

            options=[]
        )
        db.add(node)
        db.flush()

        if not node.is_ending and (
            hasattr(node_data, 'options') and node_data.options
        ):
            options_list = []
            for option_data in node_data.options:
                next_node = option_data.nextNode

                if isinstance(next_node, dict):
                    next_node = StoryNodeLLM.model_validate(next_node)

                child_node = cls._process_story_node(
                    db,
                    story_id,
                    next_node,
                    False
                )

                options_list.append({
                    'text': option_data.text,
                    'node_id': child_node.id
                })

                node_options = options_list

        db.flush()
        return node