import { NextRequest } from "next/server"
import OpenAI from 'openai';



interface Body {
    fileContents: string
    prompt: string
}

const openai = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY, // This is the default and can be omitted
});

const systemMessagePrompt = `You are a brilliant and meticulous engineer assigned to add a unit test to cover an edge case for the testing suite. When you write code, the code works on the first try, is syntactically perfect. You have the utmost care for the code that you write, so you do not make mistakes and every function. When writing tests, you will make up test data as needed. Take into account the current repository's language, frameworks, and dependencies. You are to follow the instructions exactly and do nothing more.

You can append to the file by responding in the following format:
<code_block_to_extend>
\`\`\`
The code section to add the additional unit tests right after. Ensure that you have valid indentation.
\`\`\`
</code_block_to_extend>

<additional_unit_test>
\`\`\`
The additional unit test that covers the edge case. Ensure that you have valid indentation.
\`\`\`
</additional_unit_test>`

const userMessagePrompt = `Your job is to add a unit test to the following file to complete the user's request:
<user_request>
{prompt}
</user_request>

Here is the file's current contents:
<file_contents>
{fileContents}
</file_contents>`

const unitTest = `import unittest
from unittest.mock import patch

from sweepai.utils.diff import (
    format_contents,
    is_markdown,
    match_string,
    revert_whitespace_changes,
)


class TestDiff(unittest.TestCase):
    def test_revert_whitespace_changes(self):
        original_file_str = "  line1\n  line2\n  line3"
        modified_file_str = "line1\n  line2\n    line3"
        expected_output = "  line1\n  line2\n  line3"
        self.assertEqual(
            revert_whitespace_changes(original_file_str, modified_file_str),
            expected_output,
        )

    def test_revert_whitespace_changes_more_whitespace(self):
        original_file_str = "line1\nline2\nline3"
        modified_file_str = "  line1\n  line2\n  line3"
        expected_output = "line1\nline2\nline3"
        self.assertEqual(
            revert_whitespace_changes(original_file_str, modified_file_str),
            expected_output,
        )

    def test_revert_whitespace_changes_non_whitespace_changes(self):
        original_file_str = "line1\nline2\nline3"
        modified_file_str = "line4\nline5\nline6"
        expected_output = "line1\nline2\nline3"
        self.assertEqual(
            revert_whitespace_changes(original_file_str, modified_file_str),
            expected_output,
        )

    def test_revert_whitespace_changes_same_files(self):
        original_file_str = "line1\nline2\nline3"
        modified_file_str = "line1\nline2\nline3"
        expected_output = "line1\nline2\nline3"
        self.assertEqual(
            revert_whitespace_changes(original_file_str, modified_file_str),
            expected_output,
        )

    def test_revert_whitespace_changes_empty_files(self):
        original_file_str = ""
        modified_file_str = ""
        expected_output = ""
        self.assertEqual(
            revert_whitespace_changes(original_file_str, modified_file_str),
            expected_output,
        )

    def test_revert_whitespace_changes_whitespace_only_files(self):
        original_file_str = "  \n  \n  "
        modified_file_str = "  \n  \n  "
        expected_output = "  \n  \n  "
        self.assertEqual(
            revert_whitespace_changes(original_file_str, modified_file_str),
            expected_output,
        )

    def test_format_contents(self):
        file_contents = "line1\nline2\nline3"
        expected_output = "line1\nline2\nline3"
        self.assertEqual(format_contents(file_contents), expected_output)

    @patch("sweepai.utils.diff.find_best_match")
    def test_match_string(self, mock_find_best_match):
        original = ["line1", "line2", "line3"]
        search = ["line2"]
        mock_find_best_match.return_value = 1
        self.assertEqual(match_string(original, search), 1)

    def test_is_markdown(self):
        filename = "test.md"
        self.assertTrue(is_markdown(filename))
`

const codeBlockToExtendRegex = /<code_block_to_extend>([\s\S]*)<\/code_block_to_extend>/g
const additionalUnitTestRegex = /<additional_unit_test>([\s\S]*)$/g

const callOpenAI = async (prompt: string, fileContents: string) => {
    const params: OpenAI.Chat.ChatCompletionCreateParams = {
        messages: [
            { role: 'user', content: systemMessagePrompt},
            { role: 'system', content: userMessagePrompt.replace('{prompt}', prompt).replace('{fileContents}', fileContents) }
        ],
        model: 'gpt-4-1106-preview',
    };
    const chatCompletion: OpenAI.Chat.ChatCompletion = await openai.chat.completions.create(params);
    const response = chatCompletion.choices[0].message.content!;
    console.log("response\n", response, "\n")
    const additionalUnitTestMatch = response.match(additionalUnitTestRegex)!;
    const codeBlockToExtendMatch = response.match(codeBlockToExtendRegex)!;
    if (additionalUnitTestMatch && codeBlockToExtendMatch) {
        let codeBlockToExtend = codeBlockToExtendMatch[0];
        codeBlockToExtend = codeBlockToExtend.split('\n').slice(2, -2).join('\n');
        let additionalUnitTest = additionalUnitTestMatch[0];
        additionalUnitTest = additionalUnitTest.split('\n').slice(2, -2).join('\n');
        console.log(codeBlockToExtend)
        console.log(additionalUnitTest)
        return fileContents.replace(codeBlockToExtend, codeBlockToExtend + '\n' + additionalUnitTest);
    } else {
        return null;
    }
}

export async function POST(request: NextRequest) {
    const body = await request.json() as Body;
    const response = await callOpenAI(body.prompt, unitTest);
    console.log(response)

    return Response.json({
        newFileContents: response
    })
}
