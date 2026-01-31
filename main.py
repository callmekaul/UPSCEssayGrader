from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing import TypedDict, Annotated
import operator
from dotenv import load_dotenv

load_dotenv()

class EvaluationSchema(BaseModel):
    feedback: str = Field(description="Detailed feedback on the essay")
    score: int = Field(description="Score out of 10", ge=0, le=10)

class EssayState(TypedDict):
    essay: str
    topic_relevance: str
    thought_depth: str
    structure: str
    multidimensionality: str
    examples: str
    language: str
    coherence: str
    conclusion: str
    overall: str
    scores: Annotated[list[int], operator.add]
    total_score: int

def evaluate_topic_relevance(state: EssayState):
    prompt = f"""
Evaluate the essay ONLY on topic relevance.

Scoring scale:
- 9-10: Fully and deeply addresses the topic.
- 7-8: Mostly relevant with minor digressions.
- 5-6: Broadly related but noticeable drift.
- 3-4: Partial relevance or misunderstanding.
- 0-2: Largely irrelevant.

Essay:
{state['essay']}

Return a score and feedback.
"""
    response = structured_model.invoke(prompt)
    return {
        "topic_relevance": response.feedback,
        "scores": [response.score]
    }


def evaluate_thought_depth(state: EssayState):
    prompt = f"""
Evaluate the essay ONLY for depth of thought and insight.

Scoring scale:
- 9-10: Nuanced and original reasoning.
- 7-8: Logical but predictable.
- 5-6: Basic arguments.
- 3-4: Superficial thinking.
- 0-2: No analysis.

Essay:
{state['essay']}

Return a score and feedback.
"""
    response = structured_model.invoke(prompt)
    return {
        "thought_depth": response.feedback,
        "scores": [response.score]
    }


def evaluate_structure(state: EssayState):
    prompt = f"""
Evaluate the essay ONLY for structure and organization.

Scoring scale:
- 9-10: Clear intro, logical body, strong conclusion.
- 7-8: Generally well structured.
- 5-6: Uneven structure.
- 3-4: Poor sequencing.
- 0-2: Disorganized.

Essay:
{state['essay']}

Return a score and feedback.
"""
    response = structured_model.invoke(prompt)
    return {
        "structure": response.feedback,
        "scores": [response.score]
    }

def evaluate_multidimensionality(state: EssayState):
    prompt = f"""
Evaluate the essay ONLY for multi-dimensional coverage.

Scoring scale:
- 9-10: Meaningful integration of multiple dimensions.
- 7-8: Several dimensions covered.
- 5-6: Limited dimensionality.
- 3-4: One-dimensional.
- 0-2: Extremely narrow.

Essay:
{state['essay']}

Return a score and feedback.
"""
    response = structured_model.invoke(prompt)
    return {
        "multidimensionality": response.feedback,
        "scores": [response.score]
    }

def evaluate_examples(state: EssayState):
    prompt = f"""
Evaluate the essay ONLY for examples and evidence.

Scoring scale:
- 9-10: Precise and well-integrated examples.
- 7-8: Relevant but uneven examples.
- 5-6: Generic examples.
- 3-4: Few or weak examples.
- 0-2: No examples.

Essay:
{state['essay']}

Return a score and feedback.
"""
    response = structured_model.invoke(prompt)
    return {
        "examples": response.feedback,
        "scores": [response.score]
    }

def evaluate_language(state: EssayState):
    prompt = f"""
Evaluate the essay ONLY for language quality and expression.

Scoring scale:
- 9-10: Clear, fluent, and precise.
- 7-8: Mostly clear.
- 5-6: Understandable but plain.
- 3-4: Frequent issues.
- 0-2: Very poor readability.

Essay:
{state['essay']}

Return a score and feedback.
"""
    response = structured_model.invoke(prompt)
    return {
        "language": response.feedback,
        "scores": [response.score]
    }

def evaluate_coherence(state: EssayState):
    prompt = f"""
Evaluate the essay ONLY for coherence and flow.

Scoring scale:
- 9-10: Smooth, unified argument.
- 7-8: Mostly coherent.
- 5-6: Fragmented in places.
- 3-4: Disjointed.
- 0-2: No continuity.

Essay:
{state['essay']}

Return a score and feedback.
"""
    response = structured_model.invoke(prompt)
    return {
        "coherence": response.feedback,
        "scores": [response.score]
    }

def evaluate_conclusion(state: EssayState):
    prompt = f"""
Evaluate the essay ONLY for conclusion strength.

Scoring scale:
- 9-10: Insightful and forward-looking.
- 7-8: Clear but ordinary.
- 5-6: Adequate summary.
- 3-4: Weak ending.
- 0-2: Missing or abrupt.

Essay:
{state['essay']}

Return a score and feedback.
"""
    response = structured_model.invoke(prompt)
    return {
        "conclusion": response.feedback,
        "scores": [response.score]
    }


def overall_evaluation(state: EssayState):
    total = sum(state['scores'])
    prompt = f"""
    Based on the following evaluations, provide an overall feedback for the essay:

    Topic Relevance Feedback: {state['topic_relevance']}
    Thought Depth Feedback: {state['thought_depth']}
    Structure Feedback: {state['structure']}
    Multidimensionality Feedback: {state['multidimensionality']}
    Examples Feedback: {state['examples']}
    Language Feedback: {state['language']}
    Coherence Feedback: {state['coherence']}
    Conclusion Feedback: {state['conclusion']}

    Total Score: {total} out of 80
    """
    overall_evaluation = model.invoke(prompt).content
    return {'overall': overall_evaluation, 'total_score': total}

def pretty_print(result: dict):
    print("\n--- Essay Evaluation Report ---\n")
    print(f"Essay:\n{result['essay']}\n")
    print("Individual Evaluations:")
    print(f"1. Topic Relevance: {result['topic_relevance']}")
    print(f"2. Thought Depth: {result['thought_depth']}")
    print(f"3. Structure: {result['structure']}")
    print(f"4. Multidimensionality: {result['multidimensionality']}")
    print(f"5. Examples: {result['examples']}")
    print(f"6. Language: {result['language']}")
    print(f"7. Coherence: {result['coherence']}")
    print(f"8. Conclusion: {result['conclusion']}\n")
    print(f"Overall Evaluation:\n{result['overall']}\n")
    print(f"Total Score: {result['total_score']} out of 80")
    print("\n--- End of Report ---\n")



model = ChatOpenAI(model="gpt-4o-mini")
structured_model = model.with_structured_output(EvaluationSchema)

graph = StateGraph(EssayState)

graph.add_node('evaluate_topic_relevance',evaluate_topic_relevance)
graph.add_node('evaluate_thought_depth',evaluate_thought_depth)
graph.add_node('evaluate_structure',evaluate_structure)
graph.add_node('evaluate_multidimensionality',evaluate_multidimensionality)
graph.add_node('evaluate_examples',evaluate_examples)
graph.add_node('evaluate_language',evaluate_language)
graph.add_node('evaluate_coherence',evaluate_coherence)
graph.add_node('evaluate_conclusion',evaluate_conclusion)
graph.add_node('overall_evaluation', overall_evaluation)

graph.add_edge(START, 'evaluate_topic_relevance')
graph.add_edge(START, 'evaluate_thought_depth')
graph.add_edge(START, 'evaluate_structure')
graph.add_edge(START, 'evaluate_multidimensionality')
graph.add_edge(START, 'evaluate_examples')
graph.add_edge(START, 'evaluate_language')
graph.add_edge(START, 'evaluate_coherence')
graph.add_edge(START, 'evaluate_conclusion')

graph.add_edge('evaluate_topic_relevance', 'overall_evaluation')
graph.add_edge('evaluate_thought_depth', 'overall_evaluation')
graph.add_edge('evaluate_structure', 'overall_evaluation')
graph.add_edge('evaluate_multidimensionality', 'overall_evaluation')
graph.add_edge('evaluate_examples', 'overall_evaluation')
graph.add_edge('evaluate_language', 'overall_evaluation')
graph.add_edge('evaluate_coherence', 'overall_evaluation')
graph.add_edge('evaluate_conclusion', 'overall_evaluation')
graph.add_edge('overall_evaluation', END)

workflow = graph.compile()

essay = """Human life has always been a mystery that thinkers, poets, and philosophers have tried to unravel through the ages. From the earliest civilizations to the modern world, the question of what constitutes a meaningful life has preoccupied the human mind. One of the most profound insights emerging from this reflection is the realization that life is best seen as a journey, not as a destination. To perceive life as a journey is to value growth over arrival, process over outcome, and experience over mere achievement. It is to live fully in the present moment, to embrace both joy and suffering as parts of an evolving process, and to recognize that the essence of life lies not in where we end up, but in how we travel through its varied paths. 

Across cultures and philosophies, this metaphor of life as a journey finds deep resonance. In the Indian spiritual tradition, life is often described as a yatra - a sacred pilgrimage. The Upanishads advocate the idea of “Neti Neti” - “not this, not this” - which signifies the endless quest for truth, where each realization leads to a deeper inquiry. The Buddha spoke of the “Middle Path,” not as a final point of arrival but as a continuous process of awareness and right action. In the Bhagavad Gita, Lord Krishna tells Arjuna that one has the right to perform their actions, but not to the fruits thereof. This timeless teaching captures the essence of journey-oriented living: action, sincerity, and detachment from rigid expectations. Modern thinkers have echoed this wisdom. Ralph Waldo Emerson wrote, “Life is a journey, not a destination,” while Arthur Ashe wrote that “Success is a journey, not a destination.” These reflections, both ancient and modern, underline that true fulfillment comes not from reaching an endpoint, but from constant evolution, learning, and inner growth. 

To view life as a destination, in contrast, is to see it as a race to be won, a fixed goal to be attained. It is to measure one's worth by outcomes - success, wealth, power, or recognition - rather than by integrity, learning, or happiness. The danger of such a view is that it breeds anxiety, dissatisfaction, and burnout. When people fixate on results, they often neglect the process that gives life its texture and meaning. A destination-focused mindset can make one rigid, fearful of failure, and disconnected from the joy of living. Conversely, a journey-centric approach cultivates openness, curiosity, and resilience. It allows us to enjoy the process of creation, to find purpose in progress, and to accept setbacks as integral to growth. 

Consider the stages of life - childhood, adolescence, adulthood, and old age. Each stage has its unique joys and struggles. Childhood teaches innocence and wonder; youth teaches passion and exploration; adulthood teaches responsibility and balance; and old age teaches reflection and detachment. None of these stages is a “destination” in itself; they are all milestones in an ongoing journey. To see life as a journey, therefore, is to respect the flow of time and the lessons it brings. It helps us live more consciously, without undue regret for the past or obsession with the future. 

Philosophically, this view of life has deep implications. In Eastern thought, particularly in Hinduism and Buddhism, life is cyclical, not linear. The concept of samsara - the continuous cycle of birth, death, and rebirth - implies that life itself is an eternal journey of the soul toward higher consciousness. Similarly, in Jainism, the path to liberation (moksha) is not a single act of salvation but a sustained process of self-purification through right knowledge, faith, and conduct. In the Western tradition, thinkers like Albert Camus and Jean-Paul Sartre emphasized the importance of authenticity and the acceptance of life's uncertainty. Camus's idea of the “absurd” suggests that meaning is not handed to us; it must be created through our choices and perseverance. This echoes the idea that life's purpose lies in the act of living itself, not in reaching a final, pre-defined endpoint.

In practical life, this philosophy manifests in many domains. Take education, for instance. Students who view learning as a journey derive joy from curiosity and continuous improvement, while those obsessed with grades or ranks often experience stress and disillusionment. True education, derived from the Latin educare, means “to draw out” the best in oneself. It is not about the mere accumulation of certificates, but about shaping character, intellect, and values. Similarly, in professional life, those who treat their careers as evolving journeys tend to find greater satisfaction and innovation. They adapt, learn, and grow, instead of being consumed by the pursuit of titles or monetary rewards. Success, in this sense, is not a fixed destination but a byproduct of purposeful effort and passion for one's work. 

History and contemporary examples provide ample evidence of this philosophy in action. Dr. A.P.J. Abdul Kalam's life is a shining illustration. Born in a modest family in Rameswaram, he faced numerous challenges but never saw success as a final point. His journey from a small-town boy to India's “Missile Man” and later the President was characterized by humility, constant learning, and dedication. He famously said, “Excellence is a continuous process and not an accident.” For him, the joy lay in striving for progress, not merely in the achievements that came his way. 

Mahatma Gandhi's life offers another powerful example. His journey from a timid lawyer in South Africa to the leader of India's freedom movement was not defined by a single destination. Freedom for him was not just political independence but moral and social transformation. His experiments with truth, non-violence, and self-discipline were ongoing processes of self-refinement. Similarly, Nelson Mandela's long struggle against apartheid, including 27 years in prison, was not just about attaining political office. His focus was on the journey of reconciliation, forgiveness, and building a just society. 

Even at the grassroots level, this philosophy finds resonance. Women's self-help groups like Kudumbashree in Kerala or the Amul cooperative movement in Gujarat demonstrate how empowering journeys - rather than fixating on immediate results - lead to longlasting transformation. These movements evolved through patience, community participation, and learning, proving that meaningful progress is always a process, not a single act of success.

From a social perspective, the “journey mindset” encourages inclusivity and empathy. When we understand that every individual walks a unique path, we become less judgmental and more compassionate. It also curbs unhealthy social comparison, a major cause of unhappiness in the age of social media. Today's digital world constantly projects images of success - luxury, fame, and achievement - creating an illusion that everyone else has “arrived.” This triggers the “fear of missing out” and fuels anxiety among youth. Viewing life as a journey, however, reminds us that each person's timeline is different, and that fulfillment lies in personal growth, not in keeping pace with others. 

Psychologically, this approach nurtures mindfulness and resilience. When we focus on the process, we learn to appreciate the present moment. We accept setbacks as part of the learning curve rather than as personal failures. Research in positive psychology also supports this view - individuals who value intrinsic motivation and process-oriented goals tend to have higher levels of happiness and emotional stability. The Japanese philosophy of Kaizen - continuous improvement - embodies the same idea: every small step forward matters, and perfection is a journey without end. 

In the sphere of governance and public administration, the metaphor of journey carries profound lessons. Policy-making is not about achieving a single destination but about continuous evaluation, adaptation, and refinement. A civil servant who sees governance as an evolving process will value feedback, transparency, and innovation. For example, the Swachh Bharat Mission began as an ambitious goal to make India open defecation free, but its real success depends on sustained behavioral change and community participation. Likewise, the Digital India initiative, Beti Bachao Beti Padhao, or Jal Jeevan Mission all require constant review and citizen engagement. Governance, like life, must be dynamic - a process of learning, not a static end. 

This idea also finds a deep echo in India's spiritual and cultural fabric. Festivals like the Kumbh Mela symbolize collective journeys of faith and self-discovery. The Char Dham Yatra, undertaken across the four corners of India, represents not just physical travel but the inner pilgrimage of the soul. Saints and poets have long celebrated this view. Rabindranath Tagore beautifully wrote, “The butterfly counts not months but moments, and has time enough.” Rumi, the Sufi mystic, said, “It's your road, and yours alone. Others may walk it with you, but no one can walk it for you.” Such insights remind us that the purpose of existence is not to reach an ultimate point but to experience the divinity and beauty embedded in every step. 

The modern world, however, often pulls us in the opposite direction. The obsession with speed, efficiency, and competition can make life feel like a relentless chase. Technology and globalization have intensified this pressure. Young people, in particular, face an acute dilemma: the race for degrees, jobs, or social recognition often overshadows the joy of self-discovery. The education system, too, emphasizes destinations - marks, ranks, and placements - over curiosity and critical thinking. In this context, seeing life as a journey is not just an individual choice but a social necessity. It encourages patience, creativity, and empathy - values that sustain societies in the long run. 

Critics may argue that without destinations, life lacks direction. Indeed, goals are necessary; they provide structure and motivation. But goals should serve as milestones, not final ends. A journeyoriented life does not reject ambition; it simply refuses to be enslaved by it. It balances aspiration with mindfulness, effort with acceptance. The world's greatest innovators, artists, and leaders were not driven merely by end results but by their love for the process. The Wright brothers, Thomas Edison, or Marie Curie, persisted through countless failures, not because they were fixated on a destination, but because they were enchanted by the journey of discovery itself. 

Moreover, a journey-oriented approach fosters ethical living. When people focus on how they live, rather than what they achieve, they are more likely to make morally sound choices. The process becomes as important as the outcome. This is particularly vital in public life, where the temptation to achieve results quickly can lead to ethical compromises. A civil servant or political leader who values the process - transparency, participation, and compassion - contributes more meaningfully to the nation's progress than one who only seeks immediate recognition. 

In a larger metaphysical sense, life as a journey also mirrors the universe itself. Everything in nature moves in cycles - the changing seasons, the water cycle, the rotation and revolution of planets. There is no fixed “destination” in this cosmic dance; everything is in motion, in process, in transformation. When human beings align themselves with this rhythm, they live more harmoniously and purposefully. Life then becomes not a checklist to complete, but a melody to be experienced. 

Ultimately, the philosophy of seeing life as a journey is one of liberation. It frees us from the anxiety of control and the illusion of permanence. It teaches us humility - that no achievement is final, and no failure is fatal. It deepens gratitude - for every moment, every relationship, and every opportunity to grow. It also prepares us to face the inevitable - aging, loss, and death - with grace. Death itself, in this perspective, is not an end but a transition, another step in the infinite journey of the soul. 

To live with this awareness is to live wisely. For the student striving for excellence, the civil servant serving the nation, the artist creating beauty, or the common person navigating everyday struggles, the message remains the same: the meaning of life lies in the path, not merely in the endpoint. What matters most is not how soon we reach, but how sincerely we walk. Life, therefore, is best lived as a pilgrimage - an unfolding journey of discovery, compassion, and continuous growth. 

Destinations are but temporary halts; the journey is eternal. Every success is followed by new challenges, every fulfillment by fresh desires. To see life as a journey is to accept this impermanence with courage and joy. It is to celebrate the unfolding of each moment, to learn from every twist and turn, and to move forward with hope. As T.S. Eliot wrote, “We shall not cease from exploration, and the end of all our exploring will be to arrive where we started and know the place for the first time.” Thus, the greatest wisdom lies in walking the path with awareness, gratitude, and love - for in the journey itself, we find our true destination."""

inital_state: EssayState = {
    'essay': essay
}

result = workflow.invoke(inital_state)

pretty_print(result)