prompt = f"""Question: {{question}}

Classify the above question into one of following categories from Bloom's Revised Taxonomy.

1. Remember
Definition: retrieve, recall, or recognize relevant knowledge from long-term memory (e.g., recall dates of important events in U.S. history, remember the components of a bacterial cell). Appropriate learning outcome verbs for this level include: cite, define, describe, identify, label, list, match, name, outline, quote, recall, report, reproduce, retrieve, show, state, tabulate, and tell.

2. Understand
Definition: demonstrate comprehension through one or more forms of explanation (e.g., classify a mental illness, compare ritual practices in two different religions). Appropriate learning outcome verbs for this level include: abstract, arrange, articulate, associate, categorize, clarify, classify, compare, compute, conclude, contrast, defend, diagram, differentiate, discuss, distinguish, estimate, exemplify, explain, extend, extrapolate, generalize, give examples of, illustrate, infer, interpolate, interpret, match, outline, paraphrase, predict, rearrange, reorder, rephrase, represent, restate, summarize, transform, and translate.

3. Apply
Definition: use information or a skill in a new situation (e.g., use Newton's second law to solve a problem for which it is appropriate, carry out a multivariate statistical analysis using a data set not previously encountered). Appropriate learning outcome verbs for this level include: apply, calculate, carry out, classify, complete, compute, demonstrate, dramatize, employ, examine, execute, experiment, generalize, illustrate, implement, infer, interpret, manipulate, modify, operate, organize, outline, predict, solve, transfer, translate, and use.

4. Analyze
Definition: break material into its constituent parts and determine how the parts relate to one another and/or to an overall structure or purpose (e.g., analyze the relationship between different flora and fauna in an ecological setting; analyze the relationship between different characters in a play; analyze the relationship between different institutions in a society). Appropriate learning outcome verbs for this level include: analyze, arrange, break down, categorize, classify, compare, connect, contrast, deconstruct, detect, diagram, differentiate, discriminate, distinguish, divide, explain, identify, integrate, inventory, order, organize, relate, separate, and structure.

5. Evaluate
Definition: make judgments based on criteria and standards (e.g., detect inconsistencies or fallacies within a process or product, determine whether a scientist's conclusions follow from observed data, judge which of two methods is the way to solve a given problem, determine the quality of a product based on disciplinary criteria). Appropriate learning outcome verbs for this level include: appraise, apprise, argue, assess, compare, conclude, consider, contrast, convince, criticize, critique, decide, determine, discriminate, evaluate, grade, judge, justify, measure, rank, rate, recommend, review, score, select, standardize, support, test, and validate.

6. Create
Definitions: put elements together to form a new coherent or functional whole; reorganize elements into a new pattern or structure (design a new set for a theater production, write a thesis, develop an alternative hypothesis based on criteria, invent a product, compose a piece of music, write a play). Appropriate learning outcome verbs for this level include: arrange, assemble, build, collect, combine, compile, compose, constitute, construct, create, design, develop, devise, formulate, generate, hypothesize, integrate, invent, make, manage, modify, organize, perform, plan, prepare, produce, propose, rearrange, reconstruct, reorganize, revise, rewrite, specify, synthesize, and write."""

follow_up_prompt = "Reply with only the category (Remember, Understand, Apply, Analyze, Evaluate, Create) without any other text."