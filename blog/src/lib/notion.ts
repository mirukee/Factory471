import pkg from '@notionhq/client';
const { Client } = pkg;
import { NotionToMarkdown } from 'notion-to-md';
import * as dotenv from 'dotenv';
import fs from 'fs';
import path from 'path';

// Load environment variables from .env file
dotenv.config({ path: path.resolve(process.cwd(), '.env') });

const notion = new Client({
    auth: process.env.NOTION_TOKEN,
});

const n2m = new NotionToMarkdown({ notionClient: notion });

export interface BlogPost {
    id: string;
    title: string;
    slug: string;
    date: string;
    description: string;
    tags: string[];
    coverImage: string | null;
    content?: string;
}

function getPropertyValue(property: any): string | null {
    if (!property) return null;

    switch (property.type) {
        case 'title':
            return property.title[0]?.plain_text || null;
        case 'rich_text':
            return property.rich_text[0]?.plain_text || null;
        case 'date':
            return property.date?.start || null;
        case 'multi_select':
            return property.multi_select.map((item: any) => item.name).join(', ') || null;
        case 'select':
            return property.select?.name || null;
        case 'checkbox':
            return property.checkbox ? 'Yes' : 'No';
        case 'files':
            // Return the URL of the first file/image
            if (property.files && property.files.length > 0) {
                const file = property.files[0];
                return file.type === 'external' ? file.external.url : file.file.url;
            }
            return null;
        default:
            return null;
    }
}

export async function fetchPublishedPosts(): Promise<BlogPost[]> {
    if (!process.env.NOTION_DATABASE_ID) {
        console.error("NOTION_DATABASE_ID is missing from .env");
        return [];
    }

    try {
        const response = await notion.search({
            filter: {
                property: 'object',
                value: 'page',
            },
            sort: {
                timestamp: 'last_edited_time',
                direction: 'descending',
            },
        });
        // Filter to only pages inside the target database
        const databaseId = process.env.NOTION_DATABASE_ID!.replace(/-/g, '');
        response.results = response.results.filter((page: any) =>
            page.parent?.database_id?.replace(/-/g, '') === databaseId
        );

        return response.results.map((page: any) => {
            const tempTitle = getPropertyValue(page.properties.이름) || getPropertyValue(page.properties.Name) || 'Untitled Post';

            // Extract a slug from properties, or generate from title/id
            let slug = getPropertyValue(page.properties.Slug) || getPropertyValue(page.properties.slug);
            if (!slug) {
                slug = tempTitle.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)+/g, '-');
            }

            return {
                id: page.id,
                title: tempTitle,
                slug: slug,
                date: getPropertyValue(page.properties.Date) || getPropertyValue(page.properties['생성 일시']) || page.created_time.split('T')[0],
                description: getPropertyValue(page.properties.Description) || getPropertyValue(page.properties.요약) || '',
                tags: (getPropertyValue(page.properties.Tags) || getPropertyValue(page.properties.태그) || '').split(',').map(tag => tag.trim()).filter(Boolean),
                coverImage: page.cover ? (page.cover.type === 'external' ? page.cover.external.url : page.cover.file.url) : null,
            };
        });
    } catch (error) {
        console.error("Error fetching Notion posts:", error);
        return [];
    }
}


export async function fetchPostContent(pageId: string): Promise<string> {
    try {
        const mdblocks = await n2m.pageToMarkdown(pageId);
        const mdString = n2m.toMarkdownString(mdblocks);
        return mdString.parent || "";
    } catch (error) {
        console.error("Error converting Notion page to Markdown:", error);
        return "";
    }
}
