import openai
from src.core.prompts import system_message_prompt

first_user_prompt = '''<relevant_snippets_in_repo>
<snippet filepath="src/core/vector_db.py" start="42" end="69">
secrets = [
    modal.Secret.from_name(BOT_TOKEN_NAME),
    modal.Secret.from_name("openai-secret"),
    modal.Secret.from_name("huggingface"),
    modal.Secret.from_name("chroma-endpoint"),
    modal.Secret.from_name("posthog"),
    modal.Secret.from_name("highlight"),
    modal.Secret.from_dict({"TRANSFORMERS_CACHE": MODEL_DIR}),
]

def init_deeplake_vs(repo_name):
    deeplake_repo_path = f"mem://{DEEPLAKE_FOLDER}{repo_name}"
    deeplake_vector_store = DeepLakeVectorStore(path = deeplake_repo_path)
    return deeplake_vector_store

def parse_collection_name(name: str) -> str:
    # Replace any non-alphanumeric characters with hyphens
    name = re.sub(r"[^\w-]", "--", name)
    # Ensure the name is between 3 and 63 characters and starts/ends with alphanumeric
    name = re.sub(r"^(-*\w{0,61}\w)-*$", r"\1", name[:63].ljust(3, "x"))
    return name

def list_collection_names():
    """Returns a list of all collection names."""
    collections = []
    return collections

</snippet>
<snippet filepath="src/handlers/on_ticket.py" start="188" end="235">
    human_message = HumanMessagePrompt(
        repo_name=repo_name,
        issue_url=issue_url,
        username=username,
        repo_description=repo_description,
        title=title,
        summary=summary + replies_text,
        snippets=snippets,
        tree=tree, # TODO: Anything in repo tree that has something going through is expanded
    )
    sweep_bot = SweepBot.from_system_message_content(
        human_message=human_message, repo=repo, is_reply=bool(comments)
    )

    try:
        logger.info("CoT retrieval...")
        if sweep_bot.model == "gpt-4-32k-0613":
            sweep_bot.cot_retrieval()
        logger.info("Fetching files to modify/create...")
        file_change_requests = sweep_bot.get_files_to_change()
        logger.info("Getting response from ChatGPT...")
        reply = sweep_bot.chat(reply_prompt, message_key="reply")
        sweep_bot.delete_messages_from_chat("reply")
        logger.info("Sending response...")
        new_line = '\n'
        comment_reply(
            reply
            + "\n\n"
            + collapsible_template.format(
                summary="Some code snippets I looked at (click to expand). If some file is missing from here, you can mention the path in the ticket description.",
                body="\n".join(
                    [
                        f"https://github.com/{organization}/{repo_name}/blob/{repo.get_commits()[0].sha}/{snippet.file_path}#L{max(snippet.start, 1)}-L{min(snippet.end, snippet.content.count(new_line))}\n"
                        for snippet in snippets[::-1]
                    ]
                ),
            )
        )

        logger.info("Generating PR...")
        pull_request = sweep_bot.generate_pull_request()

        logger.info("Making PR...")
        pull_request.branch_name = sweep_bot.create_branch(pull_request.branch_name)
        sweep_bot.change_files_in_github(file_change_requests, pull_request.branch_name)

        # Include issue number in PR description
</snippet>
<snippet filepath="tests/test_chatgpt.py" start="17" end="24">
expected_deletion_messages = [{'role': 'system', 
'content': 'You\'re name is Sweep bot. You are an engineer assigned to the following Github ticket. You will be helpful and friendly, but informal and concise: get to the point. You will use Github-style markdown when needed to structure your responses.\n\n\nRepo: sweepai/sweep-test: test_repo_description\nIssue: test_issue\nUsername: test_user\nTitle: test_title\nDescription: test_summary\n\nRelevant Directories:\n<relevant_directories>\ntest_file_path_a\n</relevant_directories>\n\nRelevant Files:\n<relevant_files>\n```\ntest_file_path_a\n"""\ntest_file_contents_a\n"""\n```\n</relevant_files>\n'}]

example_file_prompt = "modify test_file_contents_a"
example_file_contents_file_a = "test_file_contents_a was modified"
example_file_summary_file_a = "test_file_contents_a modified"

</snippet>
<snippet filepath="src/handlers/on_comment.py" start="25" end="41">
def on_comment(
    repo_full_name: str,
    repo_description: str,
    comment: str,
    pr_path: str | None,
    pr_line_position: int | None,
    username: str,
    installation_id: int,
    pr_number: int = None,
):
    # Flow:
    # 1. Get relevant files
    # 2: Get human message
    # 3. Get files to change
    # 4. Get file changes
    # 5. Create PR
</snippet>
<snippet filepath="tests/test_pr_diffs.py" start="102" end="115">
    summarization_reply = sweep_bot.chat(review_prompt, message_key="review")
    extracted_summary = DiffSummarization.from_string(summarization_reply)
    summarization_replies.append(extracted_summary.content)
    # comment = PullRequestComment.from_string(reply)
    for diff in diffs[1:]:
        review_message = HumanMessageReviewFollowup(diff=diff)
        review_prompt_constructed = review_message.construct_prompt()
        summarization_reply = sweep_bot.chat(review_prompt_constructed, message_key="review")
        extracted_summary = DiffSummarization.from_string(summarization_reply)
        summarization_replies.append(extracted_summary.content)
    final_review_prompt = HumanMessageFinalPRComment(summarization_replies=summarization_replies).construct_prompt()
    reply = sweep_bot.chat(final_review_prompt, message_key="final_review")
    review_coment = PullRequestComment.from_string(reply)
</snippet>
</relevant_snippets_in_repo>

<relevant_paths_in_repo>
src/core/vector_db.py
src/handlers/on_ticket.py
tests/test_chatgpt.py
src/handlers/on_comment.py
tests/test_pr_diffs.py
</relevant_paths_in_repo>

<repo_tree>
.flake8
.github/...
.gitignore
.pre-commit-config.yaml
.vscode/...
Dockerfile
LICENSE
README.md
deploy.sh
poetry.lock
pyproject.toml
src/
 |- __init__.py
 |- api.py
 |- core/
 |   |- __init__.py
 |   |- models.py
 |   |- prompts.py
 |   |- react.py
 |   |- sweep_bot.py
 |   |- vector_db.py
 |- events.py
 |- handlers/
 |   |- __init__.py
 |   |- on_comment.py
 |   |- on_review.py
 |   |- on_ticket.py
 |- utils/...
tests/
 |- chunking_experiments.ipynb
 |- create_sample_issue.py
 |- example_code/...
 |- recursive_chunking_experiments.ipynb
 |- test_cached_embedding.py
 |- test_chatgpt.py
 |- test_chunking.py
 |- test_deeplake.py
 |- test_dfs.py
 |- test_diffs.py
 |- test_gpt_functions.py
 |- test_models.py
 |- test_new_ticket.py
 |- test_pr_diffs.py
 |- test_prompt_constructor.py
 |- test_review_comments.py
 |- test_tiktoken.py
 |- test_tools.py
 |- test_tree.py
 |- test_vector_db.py
</repo_tree>

Repo: sweep: Sweep AI solves Github tickets by writing PRs
Issue Url: https://github.com/sweepai/sweep/issues/1
Username: wwzeng1
Issue Title: Sweep: Pass in comment.id to on_comment.py. Then fetch this comment object to add eyes emoji, delete the eyes emoji, and add a rocket
Issue Description: None

Modify src/handlers/on_comment.py using modify_file. Add a comment.id parameter to on_comment.py. Then fetch this comment object to add eyes emoji, delete the eyes emoji, and add a rocket.

Pass in start_line and end_line to the function.

<body file_name="on_comment.py">
1: """
2: On Github ticket, get ChatGPT to deal with it
3: """
4: 
5: # TODO: Add file validation
6: 
7: import os
8: import openai
9: 
10: from loguru import logger
11: 
12: from src.core.sweep_bot import SweepBot
13: from src.handlers.on_review import get_pr_diffs
14: from src.utils.event_logger import posthog
15: from src.utils.github_utils import (
16:     get_github_client,
17:     search_snippets,
18: )
19: from src.utils.prompt_constructor import HumanMessageCommentPrompt
20: from src.utils.constants import PREFIX
21: 
22: github_access_token = os.environ.get("GITHUB_TOKEN")
23: openai.api_key = os.environ.get("OPENAI_API_KEY")
24: 
25: 
26: def on_comment(
27:     repo_full_name: str,
28:     repo_description: str,
29:     comment: str,
30:     pr_path: str | None,
31:     pr_line_position: int | None,
32:     username: str,
33:     installation_id: int,
34:     pr_number: int = None,
35: ):
36:     # Flow:
37:     # 1. Get relevant files
38:     # 2: Get human message
39:     # 3. Get files to change
40:     # 4. Get file changes
41:     # 5. Create PR
42:     logger.info(f"Calling on_comment() with the following arguments: {comment}, {repo_full_name}, {repo_description}, {pr_path}")
43:     organization, repo_name = repo_full_name.split("/")
44:     metadata = {
45:         "repo_full_name": repo_full_name,
46:         "repo_name": repo_name,
47:         "organization": organization,
48:         "repo_description": repo_description,
49:         "installation_id": installation_id,
50:         "username": username,
51:         "function": "on_comment",
52:         "mode": PREFIX,
53:     }
54: 
55:     posthog.capture(username, "started", properties=metadata)
56:     logger.info(f"Getting repo {repo_full_name}")
57:     try:
58:         g = get_github_client(installation_id)
59:         repo = g.get_repo(repo_full_name)
60:         pr = repo.get_pull(pr_number)
61:         branch_name = pr.head.ref
62:         pr_title = pr.title
63:         pr_body = pr.body
64:         diffs = get_pr_diffs(repo, pr)
65:         snippets, tree = search_snippets(repo, comment, installation_id, branch=branch_name, num_files=5)
66:         pr_line = None
67:         pr_file_path = None
68:         if pr_path and pr_line_position:
69:             pr_file = repo.get_contents(pr_path, ref=branch_name).decoded_content.decode("utf-8")
70:             pr_lines = pr_file.splitlines()
71:             pr_line = pr_lines[min(len(pr_lines), pr_line_position) - 1]
72:             pr_file_path = pr_path.strip()
73: 
74:         logger.info("Getting response from ChatGPT...")
75:         human_message = HumanMessageCommentPrompt(
76:             comment=comment,
77:             repo_name=repo_name,
78:             repo_description=repo_description if repo_description else "",
79:             diffs=diffs,
80:             issue_url=pr.html_url,
81:             username=username,
82:             title=pr_title,
83:             tree=tree,
84:             summary=pr_body,
85:             snippets=snippets,
86:             pr_file_path=pr_file_path, # may be None
87:             pr_line=pr_line, # may be None
88:         )
89:         logger.info(f"Human prompt{human_message.construct_prompt()}")
90:         sweep_bot = SweepBot.from_system_message_content(
91:             # human_message=human_message, model="claude-v1.3-100k", repo=repo
92:             human_message=human_message, repo=repo
93:         )
94:     except Exception as e:
95:         posthog.capture(username, "failed", properties={
96:             "error": str(e),
97:             "reason": "Failed to get files",
98:             **metadata
99:         })
100:         raise e
101: 
102:     try:
103:         logger.info("Fetching files to modify/create...")
104:         file_change_requests = sweep_bot.get_files_to_change()
105: 
106:         logger.info("Making Code Changes...")
107:         sweep_bot.change_files_in_github(file_change_requests, branch_name)
108: 
109:         logger.info("Done!")
110:     except Exception as e:
111:         posthog.capture(username, "failed", properties={
112:             "error": str(e),
113:             "reason": "Failed to make changes",
114:             **metadata
115:         })
116:         raise e
117: 
118:     posthog.capture(username, "success", properties={**metadata})
119:     logger.info("on_comment success")
120:     return {"success": True}
</body>

<modify>
* src/handlers/on_comment.py: 
1. Add a parameter for `comment.id` in the `on_comment` function. 
2. Use this `comment.id` to fetch the comment object. 
3. Modify the comment's content to add an eyes emoji, then remove it, and finally add a rocket emoji.
</modify>
'''


functions = [
    {
        "name": "modify_file",
        "description": "Modifies or creates a file with code. Set modify to true if the file_name already exists.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_name": {
                    "type": "string",
                    "description": "The name of the file to modify or create."
                },
                "start_line": {
                    "type": "integer",
                    "description": "The line number where the change should start.",
                },
                "end_line": {
                    "type": "integer",
                    "description": "The line number where the change should end.",
                },
                "new_code": {
                    "type": "string",
                    "description": "The code to insert into the file."
                }
            },
            "required": ["file_name", "new_code", "start_line", "end_line"]
        }
    }
]

response = openai.ChatCompletion.create(
    model="gpt-4-32k-0613",
    messages=[
        {
            "role": "system",
            "content": system_message_prompt
        },
        {
            "role": "user",
            "content": first_user_prompt
        },
    ],
    functions=functions,
    function_call={"name": "modify_file"}
)
assistant_response = response.choices[0]
arguments = assistant_response["message"]["function_call"]["arguments"]
print(arguments)
import pdb; pdb.set_trace()


# Think step-by-step to break down the requested problem or feature, and then figure out what to change in the current codebase.
# Then, provide a list of files you would like to modify, abiding by the following:
# * Including the FULL path, e.g. src/main.py and not just main.py
# * Use a one-line, detailed, natural language instructions on what to modify, with reference to variable names
# * The list of files to create or modify may be empty, but you MUST leave the XML tags with a single list element with "* None"
# * There MUST be both create and modify XML tags
# * You may make at most 3 changes in total
# * You MUST follow the following format:

# Step-by-step chain of thoughts: 
# * Thought 1
# * Thought 2
# ...

# <create>
# * filename_1: instructions_1
# * filename_2: instructions_2
# ...
# </create>

# <modify>
# * filename_3: instructions_3
# * filename_4: instructions_4
# ...
# </modify>