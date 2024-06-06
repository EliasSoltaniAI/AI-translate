from langchain_core.prompts import ChatPromptTemplate


class TranslationPrompt:
    """
    Creates a prompt template for translation.
    """
    def __init__(self, system_message_str, human_message_str):
        self.system_message_str = system_message_str
        self.human_message_str = human_message_str

    def create_prompt(self):
        prompt = ChatPromptTemplate.from_messages([
            ('system', self.system_message_str),
            ('human', self.human_message_str)
        ])
        return prompt


class SkillDescriptionPrompt(TranslationPrompt):
    """
    Creates a prompt template for skill description translation.
    """
    def __init__(self):
        system_message_str = """
        You are an excellent multilingual translator. Translate the description to language: {language}. Use clear, professional and formal language.
        """
        human_message_str = """
        {description}
        """
        super().__init__(system_message_str, human_message_str)


class SkillNamePrompt(TranslationPrompt):
    """
    Creates a prompt template for skill name translation.
    """
    def __init__(self):
        system_message_str = """
        You are an excellent multilingual translator. You are given a skill name and a description for the skill.
        Translate the skill name to language: {language}. Do not translate skill description only skill name. Use clear, professional and formal translation for the skill name.
        """
        human_message_str = """
        skill name: {skill_name}, description:{description}
        """
        super().__init__(system_message_str, human_message_str)


class SkillNameOnlyPrompt(TranslationPrompt):
    """
    Creates a prompt template for skill name only translation.
    """
    def __init__(self):
        system_message_str = """
        You are an excellent multilingual translator. You are given a skill name.
        Translate the skill name to language: {language}. Use clear, professional and formal translation for the skill name.
        """
        human_message_str = """
        {skill_name}
        """
        super().__init__(system_message_str, human_message_str)


class TextTranslationPrompt(TranslationPrompt):
    """
    Creates a prompt template for text translation.
    """
    def __init__(self):
        system_message_str = """
        Role: You are an excellent multilingual translator. Translate the given text to language: {language}. Text might be a skill name,
        a skill description, or anything else. Translate the whole text accurately, not just interpret it. Use clear, professional, fluent, natural and formal language.
        for example if English text is "Practices being free from pride or arrogance. Develops the feeling or attitude that you have no special importance that makes you better than others. Embraces the quality or state of being humble.", it is translated to
        "Pratique d'être libre de toute fierté ou arrogance. Développe le sentiment ou l'attitude de ne pas avoir d'importance spéciale qui vous rend meilleur que les autres. Adopte la qualité ou l'état d'être humble." in French.
        Steps to take:
        1. Read the text carefully.
        2. Determine if the text is a skill name, a skill description, or something else.
        3. Translate the text to the target language. If the text is a skill name, translate only the skill name. If the text is a skill description, translate only the skill description.
        4. Ensure the translation is complete and accurately reflects the original meaning. Avoid leaving out any parts of the text.
        5. Use appropriate terminology specific to the context of the text.
        6. Double-check your translation for accuracy and completeness.
        7. Only output the translated text and nothing else.
        """
        human_message_str = """
        {text}
        """
        super().__init__(system_message_str, human_message_str)
